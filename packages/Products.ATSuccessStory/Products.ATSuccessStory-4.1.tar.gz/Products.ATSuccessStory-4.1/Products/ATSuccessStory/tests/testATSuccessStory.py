import unittest, doctest

from Products.ATSuccessStory.content.ATSuccessStory import ATSuccessStory

from Products.ATSuccessStory.tests.base import ATSuccessStoryTestCase, ATSuccessStoryFunctionalTestCase

from Products.CMFCore.utils import getToolByName

from Testing import ZopeTestCase as ztc

class testATSuccessStory(ATSuccessStoryTestCase):
    """Test-cases for class(es) ATSuccessStory."""

    def afterSetUp(self):
        self.pt = getToolByName(self.portal, 'portal_types')
    def testOnlyInATSSFolder(self):
        self.failIf(self.pt.ATSuccessStory.global_allow, 'Success stories are globally addable')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testATSuccessStory))
    suite.addTest(ztc.ZopeDocFileSuite('testATSSfunctional.txt',
                        package='Products.ATSuccessStory.tests',
                        test_class=ATSuccessStoryFunctionalTestCase,
                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                        doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))
    return suite

if __name__ == '__main__':
    framework()


