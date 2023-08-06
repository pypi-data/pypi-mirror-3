from collective.anonymousview.tests.base import TestCase
from zope.testing import doctestunit
from Testing import ZopeTestCase as ztc
import doctest
import unittest
from Products.Five.testbrowser import Browser

def test_suite():
    """This sets up a test suite that actually runs the tests in collective.anonymousview_integration.txt"""
    return unittest.TestSuite([
        ztc.FunctionalDocFileSuite(
            'tests/anonymousview_integration.txt', package='collective.anonymousview',
            test_class=TestCase),
        ])

