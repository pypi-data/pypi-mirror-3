# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope import interface

from plone.app import testing

from collective.portlet.lingualinks.testing import FUNCTIONAL_TESTING
from collective.portlet.lingualinks.testing import INTEGRATION_TESTING
from collective.portlet.lingualinks.tests import utils
from Products.LinguaPlone.browser.controlpanel import IMultiLanguageSelectionSchema


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        from ZPublisher.tests.testPublish import Request
        super(UnitTestCase, self).setUp()
        self.context = utils.FakeContext()
        self.request = Request()
        self.requestNoLayer = Request()

class TestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        super(TestCase, self).setUp()
        self.portal = self.layer['portal']
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        IMultiLanguageSelectionSchema(self.portal).available_languages(['en','fr','de'])
        self.portal.restrictedTraverse('@@language-setup-folders')()
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Member'])


class FunctionalTestCase(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        IMultiLanguageSelectionSchema(self.portal).available_languages(['en','fr','de'])
        self.portal.restrictedTraverse('@@language-setup-folders')()
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Member'])


def build_test_suite(test_classes):
    suite = unittest.TestSuite()
    for klass in test_classes:
        suite.addTest(unittest.makeSuite(klass))
    return suite
