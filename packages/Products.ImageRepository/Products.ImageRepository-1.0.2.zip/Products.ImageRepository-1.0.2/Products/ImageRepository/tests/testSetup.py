#
# FRTypes Setup Tests
#

from Products.ImageRepository.tests import ImageRepositoryTestCase


class TestSetup(ImageRepositoryTestCase.ImageRepositoryTestCase):

    def testContentTypes(self):
        types = self.portal.portal_types.objectIds()
        contents = ['ImageRepository']
        for content in contents:
            self.failUnless(content in types)

    def testSkins(self):
        portal_skins = self.portal.portal_skins.objectIds()
        skins = (
            'ImageRepository',
        )
        for skin in skins:
            self.failUnless(skin in skins)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite

if __name__ == '__main__':
    import unittest
    unittest.main()
