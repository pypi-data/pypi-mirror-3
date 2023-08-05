#-*- coding: utf-8 -*-
import os
import uuid
import shutil
import tarfile

class StorageBackup(object):
    '''Backup a file system storage'''
    
    def __init__(self, work, location, backup=False):
        '''Initialize the backup'''
        # Store the location
        self.location = location
        # Store the backup path
        self.path = os.path.join(work, '%s.tar.gz' % uuid.uuid4().hex)
        # Check if location exists or not
        self.exists = False
        # Check if backup required
        if backup: self.backup()

    def backup(self):
        '''Backup all file and folders'''
        # Check if exists
        self.exists = os.path.exists(self.location)
        # If exists, store in a tar
        if self.exists:
            # Open the tar file
            tar = tarfile.open(self.path, 'w:gz')
            # Add all under location
            tar.add(self.location, arcname=os.path.basename(self.location))
            # Close the tar
            tar.close()
    
    def restore(self):
        '''Restore data'''
        # Check if location is a folder
        if os.path.isdir(self.location):
            # Delete folder
            shutil.rmtree(self.location)
        # Check if location is a file
        elif os.path.isfile(self.location):
            # Delete file
            os.remove(self.location)
        # Check if folder was already there
        if self.exists:
            # If was there, get files from the tar
            tar = tarfile.open(self.path, 'r:gz')
            # Extract all
            tar.extractall(os.path.dirname(self.location))
            # Close file
            tar.close()

    def delete(self):
        '''Delete backup'''
        # Check if file exists
        if os.path.isfile(self.path): os.remove(self.path)
