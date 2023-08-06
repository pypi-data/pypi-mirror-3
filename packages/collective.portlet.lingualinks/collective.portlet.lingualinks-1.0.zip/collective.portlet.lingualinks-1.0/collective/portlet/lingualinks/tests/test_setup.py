# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.portlet.lingualinks.testing import INTEGRATION_TESTING
from zope import component
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping

class TestInstall(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        self.leftcolumn = component.getUtility(IPortletManager,
                                       name=u"plone.leftcolumn")

    def test_installed(self):
        self.assertTrue(self.qi.isProductInstalled('collective.portlet.lingualinks'),
                        'package not installed')

    def test_portlet_installed(self):
        addable_portlets = self.leftcolumn.getAddablePortletTypes()
        titles = [p.title for p in addable_portlets]
        self.assertIn('Lingualinks', titles)
#        assignment_mapping = component.getMultiAdapter((self.portal, manager),
#                                                   IPortletAssignmentMapping)

class TestUninstall(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.qi.uninstallProducts(products=['collective.portlet.lingualinks'])
        self.leftcolumn = component.getUtility(IPortletManager,
                                       name=u"plone.leftcolumn")

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled('collective.portlet.lingualinks'),
                         'package not uninstalled')

    def test_portlet_removed(self):
        addable_portlets = self.leftcolumn.getAddablePortletTypes()
        titles = [p.title for p in addable_portlets]
        self.assertNotIn('Lingualinks', titles)



def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
