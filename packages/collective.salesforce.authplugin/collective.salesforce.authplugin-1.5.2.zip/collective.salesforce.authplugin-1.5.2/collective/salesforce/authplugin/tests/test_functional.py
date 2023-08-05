"""This is a functional doctest test. It uses PloneTestCase and doctest
syntax. In the test itself, we use zope.testbrowser to test end-to-end
functionality, including the UI.

One important thing to note: zope.testbrowser is not JavaScript aware! For
that, you need a real browser. Look at zope.testbrowser.real and Selenium
if you require "real" browser testing.
"""

import unittest
import doctest

from Testing import ZopeTestCase as ztc

from collective.salesforce.authplugin.tests import base

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    try:
        import Products.Five.testbrowser
    except ImportError:
        print >> sys.stderr, ("WARNING: testbrowser not found - you probably"
                              "need to add Five 1.4+ to the Products folder. "
                              "testbrowser tests skipped")
        filenames = ()
    else:
        filenames = ('configuration_functional.txt',)
    return unittest.TestSuite(
        [
        
        # Here, we create a test suite passing the name of a file relative 
        # to the package home, the name of the package, and the test base 
        # class to use. Here, the base class is a full PloneTestCase, which
        # means that we get a full Plone site set up.
        
        # The actual test is in configuration_functional.txt
        # BBB: We can obviously remove this when testbrowser is Plone
        #      mainstream, read: with Five 1.4.
        
        # [Suite(os.path.basename(filename),
        #        optionflags=OPTIONFLAGS,
        #        package='Products.PloneHelpCenter.tests',
        #        test_class=PHCFunctionalTestCase)
        #  for filename in filenames]
        # 
        ztc.ZopeDocFileSuite(
            'configuration_functional.txt', package='collective.salesforce.authplugin.tests',
            test_class=base.SalesforceAuthFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
        for filename in filenames])
