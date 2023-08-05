import unittest
import doctest

from Testing import ZopeTestCase as ztc

from pfg.donationform.tests import base

test_files = ('one-page-checkout.txt', 'add-to-cart.txt')

def test_suite():
    return unittest.TestSuite([

        # Demonstrate the main content types
        ztc.ZopeDocFileSuite(
            f, package='pfg.donationform.tests',
            test_class=base.FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)

        for f in test_files
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
