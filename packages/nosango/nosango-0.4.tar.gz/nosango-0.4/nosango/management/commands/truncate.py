#-*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.sql import sql_flush
from django.core.management.color import no_style
from django.db import connections, transaction, DEFAULT_DB_ALIAS
from django.core.management.base import NoArgsCommand, CommandError

class Command(NoArgsCommand):
    
    option_list = NoArgsCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--database', action='store', dest='database', default=DEFAULT_DB_ALIAS,
            help='Nominates a database to truncate. Defaults to the "default" database.'),
    )
    
    help = 'Truncate database data by calling DELETE FROM `table` on each table.'
    
    def handle_noargs(self, **options):
        # Get the connection
        db = options.get('database', DEFAULT_DB_ALIAS)
        # Get connection
        connection = connections[db]
        # Check if interactive
        interactive = options.get('interactive')
        # The style of SQL
        self.style = no_style()
        # Check if need a confirmation
        if interactive:
            # Display the confirmation
            confirm = raw_input("""You have requested a database truncation.
This will IRREVERSIBLY DESTROY all data currently in the %r database.
Are you sure you want to do this?

    Type 'yes' to continue, or 'no' to cancel: """ % connection.settings_dict['NAME'])
        # No need
        else: confirm = 'yes'
        # This is it
        if confirm == 'yes':
            # Get flush orders
            sql_list = sql_flush(self.style, connection, only_django=False)
            # Process flush orders
            try:
                # Get a cursor
                cursor = connection.cursor()
                # Go threw the SQL request
                for sql in sql_list:
                    # Execute
                    cursor.execute(sql)
            # Get an error
            except Exception, e:
                # Roll back
                transaction.rollback_unless_managed(using=db)
                # This is an error
                raise CommandError("""Database %s couldn't be truncated.
    The full error: %s""" % (connection.settings_dict['NAME'], e))
            # Confirm
            transaction.commit_unless_managed(using=db)
        # Skip
        else: print 'Truncate cancelled.'
