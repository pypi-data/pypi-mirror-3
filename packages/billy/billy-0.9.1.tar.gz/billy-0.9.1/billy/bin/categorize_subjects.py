#!/usr/bin/env python

import os
import csv
import argparse
from collections import defaultdict

from billy import db
from billy.conf import settings, base_arg_parser
from billy.utils import metadata


def categorize_subjects(abbr, process_all):
    categorizer = defaultdict(set)
    categories_per_bill = defaultdict(int)
    uncategorized = defaultdict(int)

    filename = os.path.join(settings.BILLY_MANUAL_DATA_DIR,
                            'subjects', abbr + '.csv')
    try:
        reader = csv.reader(open(filename))

        # build category mapping
        for n,row in enumerate(reader):
            for subj in row[1:]:
                if subj:
                    subj = subj.strip()
                    if subj not in settings.BILLY_SUBJECTS:
                        raise Exception('invalid subject %s (%s - %s)' %
                                        (subj, row[0], n))
                    categorizer[row[0]].add(subj)
    except IOError:
        print 'Proceeding without', filename

    meta = metadata(abbr)
    spec = {meta['level']: abbr}
    if not process_all:
        sessions = meta['terms'][-1]['sessions']
        spec['session'] = {'$in': sessions}

    for bill in db.bills.find(spec):
        subjects = set()
        for ss in bill.get('scraped_subjects', []):
            categories = categorizer[ss]
            if not categories:
                uncategorized[ss] += 1
            subjects.update(categories)
        bill['subjects'] = list(subjects)

        # increment # of bills with # of subjects
        categories_per_bill[len(subjects)] += 1

        db.bills.save(bill, safe=True)

    print 'Categories per bill'
    print '-------------------'
    for ncats, total in sorted(categories_per_bill.items()):
        print '%s categories: %s bills' % (ncats, total)

    print 'Uncategorized'
    print '-------------'
    subjects_i = sorted([(v, k) for k, v in uncategorized.items()],
                        reverse=True)
    for n, category in subjects_i:
        print '%s,"%s"' % (n, category.encode('ascii', 'replace'))


def main():
    parser = argparse.ArgumentParser(
        description='apply subject categorization for bills',
        parents=[base_arg_parser],
        conflict_handler='resolve',
    )

    parser.add_argument('abbr', type=str, help='abbreviation for data to process')
    parser.add_argument('--all', help='update all sessions',
                        action='store_true', default=False)
    args = parser.parse_args()

    settings.update(args)

    categorize_subjects(args.abbr, args.all)


if __name__ == '__main__':
    main()
