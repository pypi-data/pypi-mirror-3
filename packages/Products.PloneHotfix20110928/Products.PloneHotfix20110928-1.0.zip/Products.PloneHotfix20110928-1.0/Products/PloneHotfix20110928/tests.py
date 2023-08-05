from Products.PloneTestCase import PloneTestCase as ptc
from Testing import ZopeTestCase as ztc
from Testing.testbrowser import Browser
from mechanize import HTTPError


ztc.installProduct('PloneHotfix20110928')
ptc.setupPloneSite()


class TestHotfix(ptc.FunctionalTestCase):
    def testAccessWebDav(self):
        browser = Browser()
        self.assertRaises(HTTPError, browser.open, 'http://nohost/plone/p_/webdav')

    def testAccessStandardModifiers(self):
        browser = Browser()
        browser.open('http://nohost/plone/portal_modifier/modules/StandardModifiers')
        self.assertEqual(browser.url, 
            'http://nohost/plone/acl_users/credentials_cookie_auth/require_login?came_from='
            'http%3A//nohost/plone/portal_modifier/modules/StandardModifiers')

def test_suite():
    import unittest, sys
    return unittest.findTestCases(sys.modules[__name__])
