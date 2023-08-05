import unittest
import doctest

from Testing import ZopeTestCase as ztc

from collective.portletpage.tests import base

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS


def test_suite():
    return unittest.TestSuite([

        # Demonstrate the main content types
        ztc.ZopeDocFileSuite(
            'tests/content.txt', package='collective.portletpage',
            test_class=base.FunctionalTestCase,
            optionflags=optionflags),

        # Demonstrate the portlet assignment
        ztc.ZopeDocFileSuite(
            'tests/portletassignment.txt', package='collective.portletpage',
            test_class=base.FunctionalTestCase,
            optionflags=optionflags),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
