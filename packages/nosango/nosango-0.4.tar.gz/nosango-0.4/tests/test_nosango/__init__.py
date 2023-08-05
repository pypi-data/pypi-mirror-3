#-*- coding: utf-8 -*-
import sys
import nose
import unittest

class TestCase(unittest.TestCase):
    '''Base test case'''
    pass

def main():
    '''Run test'''
    # Get line
    argv = list(sys.argv)
    # Add configuration
    argv.extend([
        '--verbosity=2',
        '--exe',
        '--nocapture',
    ])
    # Run test
    nose.runmodule(argv=argv)