import unittest
from zope.testing import doctest
from zope.component import testing, eventtesting
from zope.configuration import xmlconfig

import p4a.plonevideoembed.metadata

def setUp(test):
    testing.setUp()
    eventtesting.setUp()
    xmlconfig.file(
        'tests.zcml', package=p4a.plonevideoembed.metadata)

def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        'providers.txt',
        optionflags=doctest.ELLIPSIS,
        setUp=setUp, tearDown=testing.tearDown)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
