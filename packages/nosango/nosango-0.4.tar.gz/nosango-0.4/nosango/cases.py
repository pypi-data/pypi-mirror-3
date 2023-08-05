#-*- coding: utf-8 -*-
import unittest

import nosango.plugin    # Be sure to configure DJANGO_SETTINGS_MODULE

class Asserts(object):
    '''
    Be able to call asserts
    Must be used in multiple inheritance
    '''

    def __init__(self):
        assert isinstance(self, unittest.TestCase)

    def is_1_3_plus(self):
        from django import VERSION
        return VERSION[:2] >= (1, 3)

    def _get_dj_tc(self):
        from django.test.testcases import TransactionTestCase
        class DJTC(TransactionTestCase):
            def __init__(cls):
                if self.is_1_3_plus():
                    super(TransactionTestCase, cls).__init__()
            def runTest(self): pass
        return DJTC()
    
    # DJANGO Asserts
    
    def assertRedirects(self, *args, **kwargs): return self._get_dj_tc().assertRedirects(*args, **kwargs)
    
    def assertContains(self, *args, **kwargs): return self._get_dj_tc().assertContains(*args, **kwargs)
    
    def assertNotContains(self, *args, **kwargs): return self._get_dj_tc().assertNotContains(*args, **kwargs)
    
    def assertFormError(self, *args, **kwargs): return self._get_dj_tc().assertFormError(*args, **kwargs)
    
    def assertTemplateUsed(self, *args, **kwargs): return self._get_dj_tc().assertTemplateUsed(*args, **kwargs)
    
    def assertTemplateNotUsed(self, *args, **kwargs): return self._get_dj_tc().assertTemplateNotUsed(*args, **kwargs)

    def assertQuerysetEqual(self, *args, **kwargs):
        if not self.is_1_3_plus():
            raise NotImplementedError('assertQuerysetEqual')
        return self._get_dj_tc().assertQuerysetEqual(*args, **kwargs)

    def assertNumQueries(self, *args, **kwargs):
        if not self.is_1_3_plus():
            raise NotImplementedError('assertNumQueries')
        return self._get_dj_tc().assertNumQueries(*args, **kwargs)

    # Other Asserts
    
    def assertStatusCode(self, status_code, response):
        '''Assert on status code'''
        # Check status code
        self.assertEquals(response.status_code, status_code,
            "Couldn't retrieve page: Response code was %d (expected %d):\n%s" %
                (response.status_code, status_code, response))
        
    def assert404(self, response):
        '''Assert that status code is 404'''
        self.assertStatusCode(404, response)

    def assert200(self, response):
        '''Assert that status code is 200'''
        self.assertStatusCode(200, response)
    
    def assertJson(self, response):
        '''Assert that response is some JSON'''
        from django.utils import simplejson
        try: return simplejson.loads(response.content)
        except:
            self.fail('Failed to load JSON from response:\n%s' % response)
    
class TestCase(unittest.TestCase, Asserts):
    '''Classical test case with specific asserts'''
    pass
