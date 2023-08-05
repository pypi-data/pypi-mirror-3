import unittest
import doctest
from zope.component import testing
from Testing.ZopeTestCase import zopedoctest
from collective.salesforce.authplugin.tests.test_useradder import TestAuthenticationPlugin

import Products.Five
import collective.salesforce.authplugin
from Products.Five import zcml

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def setUp(test):
    testing.setUp()
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('configure.zcml', collective.salesforce.authplugin)
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocTestSuite('collective.salesforce.authplugin.encrypt',
                             setUp=setUp,
                             tearDown=testing.tearDown,
                             optionflags=optionflags),
    )
    suite.addTest(
        zopedoctest.ZopeDocFileSuite('encrypt.txt',
                                     package='collective.salesforce.authplugin',
                                     test_class=TestAuthenticationPlugin)
    )

    return suite
