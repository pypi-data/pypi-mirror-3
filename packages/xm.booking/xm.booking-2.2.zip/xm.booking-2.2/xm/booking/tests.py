import unittest

from zope.testing import doctest
from zope.testing import doctestunit
from zope.component import testing

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return unittest.TestSuite([

        doctestunit.DocTestSuite(
            module='xm.booking.browser.add',
            setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocFileSuite(
            'tests.txt',
            optionflags=OPTIONFLAGS,
            package='xm.booking.timing'),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
