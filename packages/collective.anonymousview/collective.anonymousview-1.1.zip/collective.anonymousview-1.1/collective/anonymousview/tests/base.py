"""Test setup for integration and functional tests."""

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.PloneTestCase.layer import onsetup

from Testing import ZopeTestCase as ztc
from Products.Five.testbrowser import Browser

import os

@onsetup
def setup_product():
    """Set up the package and its dependencies."""
    
    fiveconfigure.debug_mode = True
    import collective.anonymousview 
    zcml.load_config('configure.zcml', collective.anonymousview)
    fiveconfigure.debug_mode = False
    # We need to have a zserver to test the browerview
    ztc.utils.startZServer()
    
setup_product()
ptc.setupPloneSite(products=['collective.anonymousview'])

class TestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here. This applies to unit 
    test cases.
    """
    def __init__(self):
        self.portal_owner = portal_owner
        self.default_password = default_password
        
    def getLoggedInBrowser(self):
        """Returns a zope browser object"""
        browser = Browser()
        browser.open(self.portal.absolute_url())
        browser.getControl(name='__ac_name').value = self.portal_owner
        browser.getControl(name='__ac_password').value = self.default_password
        browser.getControl(name='submit').click()
        return browser

    
