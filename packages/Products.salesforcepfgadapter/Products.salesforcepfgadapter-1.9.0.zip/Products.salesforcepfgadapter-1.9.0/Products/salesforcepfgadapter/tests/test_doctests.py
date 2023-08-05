import unittest
import doctest

from Testing import ZopeTestCase as ztc

from Products.salesforcepfgadapter.tests import base

testfiles = (
    'pfg_adapter_view.txt',
    'pfg_adapter_edit.txt',
)

def test_suite():
    return unittest.TestSuite([

        # Test the control panel
        ztc.FunctionalDocFileSuite(
            f, package='Products.salesforcepfgadapter.tests',
            test_class=base.SalesforcePFGAdapterFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
        
            for f in testfiles
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
