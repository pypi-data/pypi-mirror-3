import unittest2 as unittest
import transaction

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from plone.app.testing import login

from collective.memberapproval.tests.layer import MEMBERAPPROVAL_INTEGRATION_TESTING

class ApprovalTest(unittest.TestCase):
    
    layer = MEMBERAPPROVAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

    def tearDown(self):
        # Hack the user status back to pending
        self.portal.acl_users.source_users_approval._activated_userid[TEST_USER_ID] = None
        # Not sure why you have to commit here for it to happen, but you do.
        transaction.commit()
        
    def login(self, username=TEST_USER_NAME, password=TEST_USER_PASSWORD, root=None):
        if root is None:
            root = self.portal
        login(root, username)
        portalURL = self.portal.absolute_url()
        self.browser.open(portalURL + '/login_form')
        self.browser.getControl(name='__ac_name').value = username
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='submit').click()

    def test_overrides(self):
        self.login(username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD, root=self.layer['app'])
        self.browser.open(self.portal.absolute_url()+'/@@usergroup-userprefs')
        self.failIf('Login Name' in self.browser.contents)
        self.failUnless('Only disapproved' in self.browser.contents)

    def test_approval_links(self):
        self.login(username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD, root=self.layer['app'])
        
        # The test user is initially pending
        self.browser.open(self.portal.absolute_url()+'/@@user-approved?userid='+TEST_USER_ID)
        self.assertEqual(self.browser.contents, 'pending')

        # Approve user
        self.browser.open(self.portal.absolute_url()+'/@@user-approve?userid='+TEST_USER_ID)
        self.browser.open(self.portal.absolute_url()+'/@@user-approved?userid='+TEST_USER_ID)
        self.assertEqual(self.browser.contents, 'approved')

        # Disapprove user
        self.browser.open(self.portal.absolute_url()+'/@@user-disapprove?userid='+TEST_USER_ID)
        self.browser.open(self.portal.absolute_url()+'/@@user-approved?userid='+TEST_USER_ID)
        self.assertEqual(self.browser.contents, 'disapproved')
        
    def test_plugin_works(self):
        portal = self.layer['portal']
        # user is not approved to login yet
        self.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        self.browser.open(portal.absolute_url())
        self.failIf(TEST_USER_NAME in self.browser.contents)

    def test_approval_view(self):
        portal = self.layer['portal']
        # login as site owner
        self.login(username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD, root=self.layer['app'])
        # approve TEST_USER_NAME using the approval view
        self.browser.open(portal.absolute_url()+'/@@user-approval?userid='+TEST_USER_NAME)
        # we require user ID
        self.failUnless('User "%s" does not exist'%TEST_USER_NAME in self.browser.contents)

        self.browser.open(portal.absolute_url()+'/@@user-approval?userid='+TEST_USER_ID)
        self.failUnless('User "%s" is currently pending approval'%TEST_USER_ID in self.browser.contents)
        self.browser.getControl('Approve').click()
        self.failUnless('User "%s" is currently approved'%TEST_USER_ID in self.browser.contents)
        self.browser.getControl('Disapprove').click()
        self.failUnless('User "%s" is currently disapproved'%TEST_USER_ID in self.browser.contents)

        # ok, approve again
        self.browser.getControl('Approve').click()
        # and test login
        self.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
        # check user is logged in after activation
        self.browser.open(portal.absolute_url())
        self.failUnless('/@@personal-preferences' in self.browser.contents)
