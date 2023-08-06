# -*- coding: utf-8 -*-

import unittest2 as unittest
from collective.portlet.lingualinks.tests import base
from collective.portlet.lingualinks.testing import INTEGRATION_TESTING
from zope import component
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletType, IPortletRenderer
from collective.portlet.lingualinks.portlet import Assignment, Renderer

PORTLET_NAME = "collective.portlet.lingualinks"

class TestPortlet(base.FunctionalTestCase):
    layer = INTEGRATION_TESTING

    def testInvokeAddview(self):
        portlet = component.getUtility(IPortletType,
                                       name=PORTLET_NAME)
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # This is a NullAddForm - calling it does the work
        addview()

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], Assignment))


    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = component.getUtility(IPortletManager, name='plone.rightcolumn',
                                       context=self.portal)
        assignment = Assignment()

        renderer = component.getMultiAdapter((context, request, view, manager, assignment),
                                             IPortletRenderer)
        self.failUnless(isinstance(renderer, Renderer))
        self.assertTrue(renderer.render() is not None)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
