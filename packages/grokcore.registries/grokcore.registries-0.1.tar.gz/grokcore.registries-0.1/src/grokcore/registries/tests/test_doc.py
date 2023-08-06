# -*- coding: utf-8 -*-

import sys
import doctest
import unittest
from zope.component import testing as base_testing


class FakeModule:
    """A fake module."""
    
    def __init__(self, dict):
        self.__dict = dict

    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError(name)


def setUp(test):
    test.globs['__name__'] = 'README'
    sys.modules['README'] = FakeModule(test.globs)
    base_testing.setUp(test)


def tearDown(test):
    del sys.modules[test.globs['__name__']]
    test.globs.clear()
    base_testing.tearDown(test)
    

def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                '../README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
