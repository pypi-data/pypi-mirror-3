import os
import glob
import json
import logging
from time import time
from collections import defaultdict

from billy.conf import settings
from billy.utils import metadata, term_for_session
from billy.scrape import JSONDateEncoder
from billy import db
from billy.importers.names import get_legislator_id
from billy.importers.subjects import SubjectCategorizer
from billy.importers.utils import (insert_with_id, update, prepare_obj,
                                   next_big_id, oysterize, fix_bill_id,
                                   get_committee_id)

if hasattr(settings, "ENABLE_GIT") and settings.ENABLE_GIT:
    from dulwich.repo import Repo
    from dulwich.objects import Blob
    from dulwich.objects import Tree
    from dulwich.objects import Commit, parse_timezone


import pymongo

logger = logging.getLogger('billy')


def ensure_indexes():
    # TODO: add a _current_term, _current_session index?

    # accomodates basic lookup / unique constraint on state/session/bill_id
    db.bills.ensure_index([('state', pymongo.ASCENDING),
                           ('session', pymongo.ASCENDING),
                           ('chamber', pymongo.ASCENDING),
                           ('bill_id', pymongo.ASCENDING)],
                          unique=True)

    # doc_id is used for search in conjunction with ElasticSearch
    #  sort field (date) comes first, followed by field that we do an $in on
    db.bills.ensure_index([('created_at', pymongo.DESCENDING),
                           ('versions.doc_id', pymongo.ASCENDING)])
    db.bills.ensure_index([('updated_at', pymongo.DESCENDING),
                           ('versions.doc_id', pymongo.ASCENDING)])
    db.bills.ensure_index([('action_dates.last', pymongo.DESCENDING),
                           ('versions.doc_id', pymongo.ASCENDING)])

    # common search indices
    db.bills.ensure_index([('state', pymongo.ASCENDING),
                           ('subjects', pymongo.ASCENDING),
                           ('action_dates.last', pymongo.DESCENDING)])
    db.bills.ensure_index([('state', pymongo.ASCENDING),
                           ('sponsors.leg_id', pymongo.ASCENDING),
                           ('action_dates.last', pymongo.DESCENDING)])

    # generic sort-assist indices on the action_dates
    db.bills.ensure_index([('state', pymongo.ASCENDING),
                           ('action_dates.first', pymongo.DESCENDING)])
    db.bills.ensure_index([('state', pymongo.ASCENDING),
                           ('action_dates.last', pymongo.DESCENDING)])
    db.bills.ensure_index([('state', pymongo.ASCENDING),
                           ('action_dates.passed_upper', pymongo.DESCENDING)])
    db.bills.ensure_index([('state', pymongo.ASCENDING),
                           ('action_dates.passed_lower', pymongo.DESCENDING)])

    # votes index
    db.votes.ensure_index([('_voters', pymongo.ASCENDING),
                           ('date', pymongo.ASCENDING)])


def import_votes(data_dir):
    pattern = os.path.join(data_dir, 'votes', '*.json')
    paths = glob.glob(pattern)

    votes = defaultdict(list)

    for path in paths:
        with open(path) as f:
            data = prepare_obj(json.load(f))

        # need to match bill_id already in the database
        bill_id = fix_bill_id(data.pop('bill_id'))

        votes[(data['bill_chamber'], data['session'], bill_id)].append(data)

    logger.info('imported %s vote files' % len(paths))
    return votes


git_active_repo = None
git_active_commit = None
git_active_tree = None
git_old_tree = None
HEAD = None


def git_add_bill(data):
    if not hasattr(settings, "ENABLE_GIT") or not settings.ENABLE_GIT:
        return

    global git_active_repo
    global git_active_tree
    global git_active_commit

    bill = json.dumps(data,
                      cls=JSONDateEncoder,
                      sort_keys=True,
                      indent=4)
    spam = Blob.from_string(bill)
    bid = str(data['_id'])
    git_active_repo.object_store.add_object(spam)
    git_active_tree[bid] = (0100644, spam.id)
    git_active_tree.check()
    print "added %s - %s" % (data['_id'], spam.id)


def git_commit(message):
    if not hasattr(settings, "ENABLE_GIT") or not settings.ENABLE_GIT:
        return

    print "Commiting import as '%s'" % (message)

    global git_active_repo
    global git_active_tree
    global git_old_tree
    global git_active_commit
    global HEAD
    repo = git_active_repo

    if git_old_tree == git_active_tree.id:
        # We don't wait t commit twice.
        print "Nothing new here. Bailing out."
        return

    c = git_active_commit
    c.tree = git_active_tree.id
    c.parents = [HEAD]
    repo.object_store.add_object(git_active_tree)
    c.author = c.committer = "Billy <openstates@sunlightfoundation.com>"
    c.commit_time = c.author_time = int(time())
    tz = parse_timezone("-0400")[0]
    c.commit_timezone = c.author_timezone = tz
    c.encoding = "UTF-8"
    c.message = message
    repo.object_store.add_object(c)
    repo.refs['refs/heads/master'] = c.id


def git_repo_init(gitdir):
    os.mkdir(gitdir)
    repo = Repo.init_bare(gitdir)
    blob = Blob.from_string("""Why, Hello there!

This is your friendly Legislation tracker, Billy here.

This is a git repo full of everything I write to the DB. This isn't super
useful unless you're debugging production issues.

Fondly,
   Bill, your local Billy instance.""")
    tree = Tree()
    tree.add("README", 0100644, blob.id)
    commit = Commit()
    commit.tree = tree.id
    author = "Billy <openstates@sunlightfoundation.com>"
    commit.author = commit.committer = author
    commit.commit_time = commit.author_time = int(time())
    tz = parse_timezone('-0400')[0]
    commit.commit_timezone = commit.author_timezone = tz
    commit.encoding = "UTF-8"
    commit.message = "Initial commit"
    repo.object_store.add_object(blob)
    repo.object_store.add_object(tree)
    repo.object_store.add_object(commit)
    repo.refs['refs/heads/master'] = commit.id


def git_prelod(abbr):
    if not hasattr(settings, "ENABLE_GIT") or not settings.ENABLE_GIT:
        return

    global git_active_repo
    global git_active_commit
    global git_active_tree
    global git_old_tree
    global HEAD

    gitdir = "%s/%s.git" % (settings.GIT_PATH, abbr)

    if not os.path.exists(gitdir):
        git_repo_init(gitdir)

    git_active_repo = Repo(gitdir)
    git_active_commit = Commit()
    HEAD = git_active_repo.head()
    commit = git_active_repo.commit(HEAD)
    tree = git_active_repo.tree(commit.tree)
    git_old_tree = tree.id
    git_active_tree = tree


def oysterize_version(bill, version):
    titles = [bill['title']] + bill.get('alternate_titles', [])
    logger.info('{0} tracked in oyster'.format(version['doc_id']))
    oysterize(version['url'], bill['state'] + ':billtext',
              id=version['doc_id'],
              # metadata
              mimetype=version.get('mimetype', None),
              titles=titles,
              state=bill['state'], session=bill['session'],
              chamber=bill['chamber'], bill_id=bill['bill_id'],
              subjects=bill.get('subjects', []),
              sponsors=[s['leg_id'] for s in bill['sponsors']],
             )


def import_bill(data, votes, categorizer):
    level = data['level']
    abbr = data[level]

    # clean up bill_ids
    data['bill_id'] = fix_bill_id(data['bill_id'])
    if 'alternate_bill_ids' in data:
        data['alternate_bill_ids'] = [fix_bill_id(bid) for bid in
                                      data['alternate_bill_ids']]

    # move subjects to scraped_subjects
    # NOTE: intentionally doesn't copy blank lists of subjects
    # this avoids the problem where a bill is re-run but we can't
    # get subjects anymore (quite common)
    subjects = data.pop('subjects', None)
    if subjects:
        data['scraped_subjects'] = subjects

    # update categorized subjects
    if categorizer:
        categorizer.categorize_bill(data)

    # this is a hack added for Rhode Island where we can't
    # determine the full bill_id, if this key is in the metadata
    # we just use the numeric portion, not ideal as it won't work
    # in states where HB/SBs overlap, but in RI they never do
    if metadata(abbr).get('_partial_vote_bill_id'):
        # pull off numeric portion of bill_id
        numeric_bill_id = data['bill_id'].split()[1]
        bill_votes = votes.pop((data['chamber'], data['session'],
                                numeric_bill_id), [])
    else:
        # add loaded votes to data
        bill_votes = votes.pop((data['chamber'], data['session'],
                                data['bill_id']), [])

    data['votes'].extend(bill_votes)

    bill = db.bills.find_one({'level': level, level: abbr,
                              'session': data['session'],
                              'chamber': data['chamber'],
                              'bill_id': data['bill_id']})

    # keep vote/doc ids consistent
    vote_matcher = VoteMatcher(abbr)
    doc_matcher = DocumentMatcher(abbr)
    if bill:
        vote_matcher.learn_ids(bill['votes'])
        doc_matcher.learn_ids(bill['versions'] + bill['documents'])
    vote_matcher.set_ids(data['votes'])
    doc_matcher.set_ids(data['versions'] + data['documents'])

    # match sponsor leg_ids
    for sponsor in data['sponsors']:
        # use sponsor's chamber if specified
        id = get_legislator_id(abbr, data['session'], sponsor.get('chamber'),
                               sponsor['name'])
        sponsor['leg_id'] = id
        if id is None:
            cid = get_committee_id(level, abbr, data['chamber'],
                                   sponsor['name'])
            if not cid is None:
                sponsor['committee_id'] = cid

    # process votes
    for vote in data['votes']:

        # committee_ids
        if 'committee' in vote:
            committee_id = get_committee_id(level, abbr, vote['chamber'],
                                            vote['committee'])
            vote['committee_id'] = committee_id

        # vote leg_ids
        for vtype in ('yes_votes', 'no_votes', 'other_votes'):
            svlist = []
            for svote in vote[vtype]:
                id = get_legislator_id(abbr, data['session'],
                                       vote['chamber'], svote)
                svlist.append({'name': svote, 'leg_id': id})

            vote[vtype] = svlist

    # process actions
    dates = {'first': None, 'last': None, 'passed_upper': None,
             'passed_lower': None, 'signed': None}
    for action in data['actions']:
        adate = action['date']

        def _match_committee(name):
            return get_committee_id(level, abbr, action['actor'], name)

        def _match_legislator(name):
            return get_legislator_id(abbr,
                                     data['session'],
                                     action['actor'],
                                     name)

        resolvers = {
            "committee": _match_committee,
            "legislator": _match_legislator
        }

        if "related_entities" in action:
            for entity in action['related_entities']:
                try:
                    resolver = resolvers[entity['type']]
                except KeyError as e:
                    # We don't know how to deal.
                    logger.error("I don't know how to sort a %s" % e)
                    continue

                id = resolver(entity['name'])
                entity['id'] = id

        # first & last
        if not dates['first'] or adate < dates['first']:
            dates['first'] = adate
        if not dates['last'] or adate > dates['last']:
            dates['last'] = adate

        # passed & signed
        if (not dates['passed_upper'] and action['actor'] == 'upper'
            and 'bill:passed' in action['type']):
            dates['passed_upper'] = adate
        elif (not dates['passed_lower'] and action['actor'] == 'lower'
            and 'bill:passed' in action['type']):
            dates['passed_lower'] = adate
        elif (not dates['signed'] and 'governor:signed' in action['type']):
            dates['signed'] = adate

    # save action dates to data
    data['action_dates'] = dates

    data['_term'] = term_for_session(abbr, data['session'])

    alt_titles = set(data.get('alternate_titles', []))

    for version in data['versions']:
        # push versions to oyster
        if settings.ENABLE_OYSTER and 'url' in version:
            oysterize_version(data, version)

        # Merge any version titles into the alternate_titles list
        if 'title' in version:
            alt_titles.add(version['title'])
        if '+short_title' in version:
            alt_titles.add(version['+short_title'])
    try:
        # Make sure the primary title isn't included in the
        # alternate title list
        alt_titles.remove(data['title'])
    except KeyError:
        pass
    data['alternate_titles'] = list(alt_titles)

    if not bill:
        bill_id = insert_with_id(data)
        git_add_bill(data)
        denormalize_votes(data, bill_id)
        return "insert"
    else:
        git_add_bill(bill)
        update(bill, data, db.bills)
        denormalize_votes(bill, bill['_id'])
        return "update"


def import_bills(abbr, data_dir):
    data_dir = os.path.join(data_dir, abbr)
    pattern = os.path.join(data_dir, 'bills', '*.json')

    git_prelod(abbr)

    counts = {
        "update": 0,
        "insert": 0,
        "total": 0
    }

    votes = import_votes(data_dir)
    try:
        categorizer = SubjectCategorizer(abbr)
    except Exception as e:
        logger.debug('Proceeding without subject categorizer: %s' % e)
        categorizer = None

    paths = glob.glob(pattern)
    for path in paths:
        with open(path) as f:
            data = prepare_obj(json.load(f))

        counts["total"] += 1
        ret = import_bill(data, votes, categorizer)
        counts[ret] += 1

    logger.info('imported %s bill files' % len(paths))

    for remaining in votes.keys():
        logger.debug('Failed to match vote %s %s %s' % tuple([
            r.encode('ascii', 'replace') for r in remaining]))

    meta = db.metadata.find_one({'_id': abbr})
    level = meta['level']
    populate_current_fields(level, abbr)

    git_commit("Import Update")

    ensure_indexes()

    return counts


def populate_current_fields(level, abbr):
    """
    Set/update _current_term and _current_session fields on all bills
    for a given location.
    """
    meta = db.metadata.find_one({'_id': abbr})
    current_term = meta['terms'][-1]
    current_session = current_term['sessions'][-1]

    for bill in db.bills.find({'level': level, level: abbr}):
        if bill['session'] == current_session:
            bill['_current_session'] = True
        else:
            bill['_current_session'] = False

        if bill['session'] in current_term['sessions']:
            bill['_current_term'] = True
        else:
            bill['_current_term'] = False

        db.bills.save(bill, safe=True)


def denormalize_votes(bill, bill_id):
    # remove all existing votes for this bill
    db.votes.remove({'bill_id': bill_id}, safe=True)

    # add votes
    for vote in bill.get('votes', []):
        vote = vote.copy()
        vote['_id'] = vote['vote_id']
        vote['bill_id'] = bill_id
        vote['state'] = bill['state']
        vote['_voters'] = [l['leg_id'] for l in vote['yes_votes']]
        vote['_voters'] += [l['leg_id'] for l in vote['no_votes']]
        vote['_voters'] += [l['leg_id'] for l in vote['other_votes']]
        db.votes.save(vote, safe=True)


class GenericIDMatcher(object):

    def __init__(self, abbr):
        self.abbr = abbr
        self.ids = {}

    def _reset_sequence(self):
        self.seq_for_key = defaultdict(int)

    def _get_next_id(self):
        return next_big_id(self.abbr, self.id_letter, self.id_collection)

    def nondup_key_for_item(self, item):
        # call user's key_for_item
        key = self.key_for_item(item)
        # running count of how many of this key we've seen
        seq_num = self.seq_for_key[key]
        self.seq_for_key[key] += 1
        # append seq_num to key to avoid sharing key for multiple items
        return key + (seq_num,)

    def learn_ids(self, item_list):
        """ read in already set ids on objects """
        self._reset_sequence()
        for item in item_list:
            key = self.nondup_key_for_item(item)
            self.ids[key] = item[self.id_key]

    def set_ids(self, item_list):
        """ set ids on an object, using internal mapping then new ids """
        self._reset_sequence()
        for item in item_list:
            key = self.nondup_key_for_item(item)
            item[self.id_key] = self.ids.get(key) or self._get_next_id()


class VoteMatcher(GenericIDMatcher):
    id_letter = 'V'
    id_collection = 'vote_ids'
    id_key = 'vote_id'

    def key_for_item(self, vote):
        return (vote['motion'], vote['chamber'], vote['date'],
                vote['yes_count'], vote['no_count'], vote['other_count'])


class DocumentMatcher(GenericIDMatcher):
    id_letter = 'D'
    id_collection = 'document_ids'
    id_key = 'doc_id'

    def key_for_item(self, document):
        # URL is good enough as a key
        return (document['url'],)
