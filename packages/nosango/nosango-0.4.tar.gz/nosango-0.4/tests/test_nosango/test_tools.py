#-*- coding: utf-8 -*-
import os
import re

import test_nosango

import nosango.tools

class TestTools(test_nosango.TestCase):
    
    def setUp(self):
        super(TestTools, self).setUp()
        self.folder = os.path.dirname(os.path.abspath(__file__))
    
    def test_huntdown_one(self):
        base = os.path.join(self.folder, 'test_tools', '1')
        self.assertEquals(
            [os.path.join(base, 'foo'), ],
            nosango.tools.huntdown(base, 'toto.dat', re.compile('foo')),
        )
        
    def test_huntdown_two(self):
        base = os.path.join(self.folder, 'test_tools', '2')
        self.assertEquals(
            [base, os.path.join(base, 'foo'), ],
            nosango.tools.huntdown(base, 'toto.dat', re.compile('foo')),
        )
        
if __name__ == '__main__':
    test_nosango.main()