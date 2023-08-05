import doctest
import unittest

from zope.testing import doctestunit
from zope.component import testing

def test_suite():
    return unittest.TestSuite([
        doctestunit.DocTestSuite('p4a.plonevideoembed.content'),

        doctestunit.DocFileSuite('plonevideoembed.txt',
                                 package='p4a.plonevideoembed',
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown),
        doctestunit.DocFileSuite('sitesetup.txt',
                                 package='p4a.plonevideoembed',
                                 optionflags=doctest.ELLIPSIS,
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
