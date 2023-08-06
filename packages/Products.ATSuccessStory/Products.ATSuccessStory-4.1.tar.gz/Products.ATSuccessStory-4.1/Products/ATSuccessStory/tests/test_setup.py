"""Test site setup
"""

import unittest
from Products.ATSuccessStory.tests.base import ATSuccessStoryTestCase

from Products.CMFCore.utils import getToolByName

class TestSetup(ATSuccessStoryTestCase):
    """Test cases for the generic setup of the product."""

    def afterSetUp(self):
        ids = self.portal.objectIds()

    def test_tools(self):
        ids = self.portal.objectIds()
        self.failUnless('archetype_tool' in ids)


    def test_types(self):
        ids = self.portal.portal_types.objectIds()
        self.failUnless('Document' in ids)

    def test_skins(self):
        ids = self.portal.portal_skins.objectIds()
        self.failUnless('plone_templates' in ids)

    def test_workflows(self):
        ids = self.portal.portal_workflow.objectIds()
        self.failUnless('plone_workflow' in ids)

    def test_workflowChains(self):
        getChain = self.portal.portal_workflow.getChainForPortalType
        self.failUnless(('plone_workflow' in getChain('Document')) or ('simple_publication_workflow' in getChain('Document')))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
