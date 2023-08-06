from billy.commands import BaseCommand

from django.conf import settings
from django.core import management

class Serve(BaseCommand):
    name = 'serve'
    help = 'run a local development server'

    def handle(self, args):
        settings.configure(DEBUG=True, TIME_ZONE='UTC', SITE_ID=1,
                           USE_I18N=False,
                           TEMPLATE_LOADERS=(
                       'django.template.loaders.filesystem.load_template_source',
                       'django.template.loaders.app_directories.load_template_source',
                           ),
                           ROOT_URLCONF='billy.site.urls',
                           INSTALLED_APPS=('django.contrib.humanize',
                                           'billy.site.api',
                                           'billy.site.browse',
                                           'billy.site.www',
                                          ),
                           DATE_FORMAT='Y-m-d',
                           TIME_FORMAT='H:i:s',
                           DATETIME_FORMAT='Y-m-d H:i:s',
                           USE_LOCKSMITH=False,
                          )

        management.call_command('runserver')
