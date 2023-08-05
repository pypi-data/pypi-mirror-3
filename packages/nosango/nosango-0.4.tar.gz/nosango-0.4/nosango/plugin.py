#-*- coding: utf-8 -*-
import os
import re
import sys
import shutil
import logging
import tempfile

from nose.plugins import Plugin
from nose.importer import add_path

from nosango.storage import StorageBackup
from nosango.tools import huntup, huntdown

# Get a logger
log =  logging.getLogger('nose.%s' % __name__)

def configure():
    '''Set settings'''
    # Store the settings
    test_settings = os.environ.get('NOSANGO_SETTINGS_MODULE')
    # Check if found
    if not test_settings:
        # Set the test settings
        test_settings = 'settings'
        # Get the base name to search
        bn = '%s.py' % test_settings
        # If not, search for the settings file
        folder = huntup(os.getcwd(), bn)
        # Check if found
        if not folder:
            # Get the pattern to search down
            pattern = re.compile(os.environ.get('NOSE_TESTMATCH', r'(?:^|[\b_\.%s-])[Tt]est' % os.sep))
            # Search down
            folders = huntdown(os.getcwd(), bn, pattern)
            # If not found, fail
            if len(folders) == 0:
                # Log
                log.warning('failed to find test settings, please specify it with NOSANGO_SETTINGS_MODULE.')
                # Not available
                return
            # Check if more than one
            elif len(folders) > 1:
                # Warning
                log.warning('found more than one %s' % bn)
            # Get first one
            folder = folders[0]
        # Log
        log.info('execute with following settings: %s' % os.path.join(folder, bn))
        # Add to nose path
        add_path(folder)
        # Add to system path
        sys.path.insert(0, folder)
    # Set in environ
    os.environ['DJANGO_SETTINGS_MODULE'] = test_settings

# Configure
configure()

class Nosango(Plugin, object):
    '''Django's test plug-in for Nose'''

    def help(self):
        '''Help'''
        return "Django's test plug-in for Nose"

    def begin(self):
        '''Configure test environment'''
        # Get the classical runner
        from django.conf import settings
        from django.db import connections, models
        from django.core.management import call_command
        from django.db.models.fields.files import FileField
        from django.test.simple import DjangoTestSuiteRunner
        from django.core.files.storage import FileSystemStorage
        # Add NOSANGO to application list
        settings.INSTALLED_APPS += ('nosango', )
        # Get work folder
        self.work = tempfile.mkdtemp()
        # Log
        log.info('work folder: %s' % self.work)
        # Get the locations
        self.locations = []
        # Go threw the models
        for model in models.get_models():
            # Get the fields to translate
            for location in [ os.path.normpath(field.storage.location) for field in model._meta.fields if isinstance(field, FileField) and isinstance(field.storage, FileSystemStorage) ]:
                # Check if not already in list
                if location not in self.locations: self.locations.append(location)
        # File system backups before database creation
        self.ibackups = [ StorageBackup(self.work, location, backup=True) for location in self.locations ]
        # Make it an helper
        self.helper = DjangoTestSuiteRunner(verbosity=self.conf.verbosity, interactive=False)
        # Create test environment
        self.helper.setup_test_environment()
        # Create databases
        self.old_config = self.helper.setup_databases()
        # If south installed, perform all migrations
        if 'south' in settings.INSTALLED_APPS:
            # Go threw the databases
            for alias in connections:
                # Get the connection
                connection = connections[alias]
                # Check that this is not a mirror
                if not connection.settings_dict['TEST_MIRROR']:
                    # Migrate
                    call_command('migrate', verbosity=self.conf.verbosity, database=alias)
        # Store backups
        self.fixtures = {}
        # Backup database
        for alias in connections:
            # Get the connection
            connection = connections[alias]
            # Check that this is not a mirror
            if not connection.settings_dict['TEST_MIRROR']:
                # Flush output
                sys.stdout.flush()
                # Backup standard output
                stdout_backup = sys.stdout
                # Get fixture path
                fixture = os.path.join(self.work, '%s.json' % alias)
                # Store it
                self.fixtures[alias] = fixture
                # Open this file
                fd = open(fixture, 'w')
                # Replace standard output
                sys.stdout = fd
                # Be able to restore data
                try: call_command('dumpdata', database=alias, format='json', indent=4)
                # Restore data
                finally:
                    # Set standard output back
                    sys.stdout = stdout_backup
                    # Close file
                    fd.close()
        # File system backups
        self.backups = [ StorageBackup(self.work, location, backup=True) for location in self.locations ]

    def beforeTest(self, test):
        '''Called before each test'''
        # Get package at runtime
        from django.core import mail
        from django.conf import settings
        from django.contrib.sites.models import Site
        from django.core.management import call_command
        from django.db import connections, DEFAULT_DB_ALIAS
        from django.core.urlresolvers import clear_url_caches
        # Backup URLs configuration
        self.old_root_urlconf = None
        # Clean site cache
        Site.objects.clear_cache()
        # Clean E-mail box
        mail.outbox = []
        # Check if test has a context
        if hasattr(test, 'context'):
            # Check if use more than one database
            if getattr(test.context, 'multi_db', False): databases = connections
            # Else use default
            else: databases = [ DEFAULT_DB_ALIAS, ]
            # Go threw the databases
            for alias in databases:
                # Clean all data in it
                call_command('truncate', verbosity=0, interactive=False, database=alias)
                # Reload backup data
                call_command('restore', *[ self.fixtures[alias] ], **{'verbosity': 0, 'database': alias})
                # Check if extra fixtures
                if getattr(test.context, 'fixtures', False):
                    # Load extra fixtures
                    call_command('loaddata', *test.context.fixtures, **{'verbosity': 0, 'database': alias})
            # Check if specific URLs
            if getattr(test.context, 'urls', False):
                # Backup previous URLs
                self.old_root_urlconf = settings.ROOT_URLCONF
                # Enable new ones
                settings.ROOT_URLCONF = test.context.urls
                # Clean the cache
                clear_url_caches()
        # Restore all
        for backup in self.backups: backup.restore()

    def afterTest(self, test):
        '''Called after each test'''
        # Get package at runtime
        from django.core import mail
        from django.conf import settings
        from django.contrib.sites.models import Site
        from django.core.urlresolvers import clear_url_caches
        # If URLs configuration was changed, restore it
        if self.old_root_urlconf is not None:
            # Restore URLs
            settings.ROOT_URLCONF = self.old_root_urlconf
            # Clear cache
            clear_url_caches()
        # Clean site cache
        Site.objects.clear_cache()
        # Clean E-mail box
        mail.outbox = []

    def finalize(self, result):
        '''Cleanup'''
        # Clean databases
        self.helper.teardown_databases(self.old_config)
        # Clean environment
        self.helper.teardown_test_environment()
        # Clean post database creation backups
        for backup in self.backups: backup.delete()
        # Restore and clean backup done before database creation
        for backup in self.ibackups:
            # Restore
            backup.restore()
            # Delete it
            backup.delete()
        # Clean work folder
        shutil.rmtree(self.work)

