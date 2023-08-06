from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from collective.installedpackages.config import PACKAGE_NAME
from collective.installedpackages.testing import INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing.interfaces import TEST_USER_ID, TEST_USER_ROLES
import sys
import unittest2 as unittest
import re

KNOWN_PACKAGES = [
    PACKAGE_NAME,
    'Products.CMFPlone',
    'Zope2',
    'ZODB3',
    'plone.testing',
    'plone.app.testing',
    'yolk',    
]

class InstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING    
    
    def setUp(self):
        self.portal = self.layer['portal']    
    
    def test_list_python_packages_view_should_list_installed_packages(self):
        view = self.portal.unrestrictedTraverse('@@list-python-packages')
        html = view()
        
        # See if headers are present.
        self.assertTrue('Name' in html)
        self.assertTrue('Platform' in html)
        self.assertTrue('Location' in html)

        # Check some known packages.
        for p in KNOWN_PACKAGES:        
            self.assertTrue(p in html)
    
    def test_list_python_packages_cfg_view_should_list_installed_packages(self):
        view = self.portal.unrestrictedTraverse('@@list-python-packages-cfg')
        html = view()
        
        # See if headers are present.
        self.assertTrue(html.startswith('[versions]'))

        # Check some known packages.
        for p in KNOWN_PACKAGES:
            self.assertIsNotNone(re.search(r'^%s = \S+$' % p, html, re.MULTILINE), p)
            
    def test_list_sys_path_view_should_list_sys_path(self):
        view = self.portal.unrestrictedTraverse('@@list-sys-path')
        html = view()
                
        for p in sys.path:
            self.assertTrue(p in html)
    
    def test_installed_packages_controlpanel_view_should_link_to_other_views(self):
        view = self.portal.unrestrictedTraverse('@@installed-packages-controlpanel')
        html = view()
                
        self.assertTrue('@@list-python-packages' in html)
        self.assertTrue('@@list-python-packages-cfg' in html)
        self.assertTrue('@@list-sys-path' in html)
        
            
    def test_views_should_be_visible_only_to_managers(self):
        mtool = getToolByName(self.portal, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        
        assert_unauthorized = lambda view: self.assertRaises(
            Unauthorized, 
            self.portal.restrictedTraverse, 
            view
        )
        assert_authorized = lambda view: self.portal.restrictedTraverse(view)()
        
        
        self.assertNotIn('Manager', user.getRoles())        
        assert_unauthorized('@@list-python-packages')
        assert_unauthorized('@@list-python-packages-cfg')
        assert_unauthorized('@@list-sys-path')
        assert_unauthorized('@@installed-packages-controlpanel')
                
        setRoles(self.portal, TEST_USER_ID, list(TEST_USER_ROLES) + ['Manager'])
        user = mtool.getAuthenticatedMember()
        
        self.assertIn('Manager', user.getRoles())
        assert_authorized('@@list-python-packages')
        assert_authorized('@@list-python-packages-cfg')
        assert_authorized('@@list-sys-path')
        assert_authorized('@@installed-packages-controlpanel')
        
        
        
        