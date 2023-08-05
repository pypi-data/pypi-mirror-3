#-*- coding: utf-8 -*-
import os
import re

def huntup(folder, bn):
    '''Search a file from the provided folder and in its parents if not found'''
    # Loop
    while folder:
        # Check if found
        if bn in os.listdir(folder): return folder
        # If not, get parent
        folder = os.path.split(folder)[0]
        # Check if reached the root
        if ( os.name == 'nt' and re.match(r'^[a-zA-Z]:\\$', folder) ) or folder == '/':
            # Failed
            return None
    # Not found, failed
    return None

def huntdown(folder, bn, pattern):
    '''Search a file from the provided folder and in its children folder matching the provided pattern'''
    # Get the folders
    results = []
    # Loop
    for root, folders, files in os.walk(folder):
        # Get the folders to do not 
        drops = [ fn for fn in folders if not pattern.search(fn) ]
        # Cleanup
        for drop in drops: folders.remove(drop)
        # Check if file exists
        if os.path.isfile(os.path.join(root, bn)):
            # Add to results
            results.append(root)
    # Return results
    return results

        

