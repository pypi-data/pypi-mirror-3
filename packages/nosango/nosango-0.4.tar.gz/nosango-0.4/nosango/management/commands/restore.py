#-*- coding: utf-8 -*-
from django.db.models import signals
from django.dispatch.dispatcher import Signal
from django.core.management.commands import loaddata

class Command(loaddata.Command):

    help = 'Installs the named fixture(s) in the database without sending signals.'

    def handle(self, *fixture_labels, **options):
        # Backup current signals
        backup = {}
        # Go threw the signal definition
        for name in dir(signals):
            # Get the instance
            signal = getattr(signals, name)
            # Check if this is a signal
            if isinstance(signal, Signal):
                # Backup receivers of the signal
                backup[signal] = signal.receivers
                # Set no receivers
                signal.receivers = []
        # Load data
        loaddata.Command.handle(self, *fixture_labels, **options)
        # Go threw backup
        for signal, receivers in backup.items():
            # And restore receivers
            signal.receivers = receivers
        
        