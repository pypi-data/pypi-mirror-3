import unittest

from Products.ATSuccessStory.content.ATSuccessStoryFolder import ATSuccessStoryFolder

from Products.ATSuccessStory.tests.base import ATSuccessStoryTestCase, ATSuccessStoryFunctionalTestCase

from Products.CMFCore.utils import getToolByName

class testATSuccessStoryFolder(ATSuccessStoryTestCase):
    """Test-cases for class(es) ATSuccessStoryFolder."""

    def afterSetUp(self):
        self.pt = getToolByName(self.portal, 'portal_types')

    def testOnlyAllowSS(self):
        self.assertEquals(self.pt.ATSuccessStoryFolder.allowed_content_types, ('ATSuccessStory',), 'ATSuccessStoryFolder is allowing %s types' %str(self.pt.ATSuccessStoryFolder.allowed_content_types))

    def testDefaultView(self):
        self.assertEquals(self.pt.ATSuccessStoryFolder.default_view, 'summary_view', 'Default view for ATSuccessStoryFolder is not "summary_view"')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testATSuccessStoryFolder))
    return suite

if __name__ == '__main__':
    framework()


