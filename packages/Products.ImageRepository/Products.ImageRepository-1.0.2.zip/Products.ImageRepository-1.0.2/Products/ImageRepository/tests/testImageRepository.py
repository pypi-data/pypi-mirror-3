#
# ImageRepositoryTestCase Skeleton
#

from Products.ImageRepository.tests import ImageRepositoryTestCase
from Products.CMFPlone.utils import _createObjectByType

from Products.ImageRepository.tests.utils import loadImage


images = [ {'id':'blue','file':'dot_blue.gif','keywords':('color','primary','serious')}
         , {'id':'green','file':'dot_gree.gif','keywords':('color','primary','nice')}
         , {'id':'purple','file':'dot_purp.gif','keywords':('color','serious')}]

templatetext = '<html metal:define-macro="master"><head metal:use-macro="here/global_defines/macros/defines"></head><body metal:define-macro="main"><metal:bt define-slot="main"></metal:bt></body></html>'

class TestImageRepository(ImageRepositoryTestCase.ImageRepositoryTestCase):

    def afterSetUp(self):
        self.repository = _createObjectByType('ImageRepository', self.portal, 'repository')
        self.repository.at_post_create_script()
        self.repositorypath = '/' + self.repository.absolute_url(1)
        for image in images:
            _createObjectByType('Image', self.repository, image['id'], image=loadImage(image['file']), subject=image['keywords'])
        self.portal.manage_addProduct['PageTemplates'].manage_addPageTemplate('main_template', 'Main', templatetext)

    def testTestSetup(self):
        # existance of the repository
        self.failUnless('repository' in self.portal.objectIds())
        # test existance of images
        ids = self.repository.objectIds()
        for image in images:
            self.failUnless(image['id'] in ids)
            obj = getattr(self.repository, image['id'])
            self.assertEqual(obj.Subject(), image['keywords'])

    def testGetUniqueKeywordsFromResults(self):
        results = self.portal.portal_catalog(portal_type='Image')
        repository = self.repository.restrictedTraverse('@@image_repository_view')
        uniquekeywords = repository.getUniqueKeywordsFromResults(results)
        keywords = (('color',3), ('primary',2), ('serious',2), ('nice',1))
        self.assertEqual(len(keywords),len(uniquekeywords))
        for keyword in keywords:
            self.failUnless(uniquekeywords.has_key(keyword[0]))
            self.assertEqual(uniquekeywords[keyword[0]], keyword[1])

    def testQueryImageRepository(self):
        REQUEST = {'keywords':['nice']}
        repository = self.repository.restrictedTraverse('@@image_repository_view')
        results = repository.queryImageRepository(REQUEST=REQUEST)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].getId, 'green')

    def testGetSearchKeywordsFromResults(self):
        REQUEST = {'keywords':['primary']}
        repository = self.repository.restrictedTraverse('@@image_repository_view')
        results = repository.queryImageRepository(REQUEST=REQUEST)
        uniquekeywords = repository.getSearchKeywordsFromResults(results)
        keywords = ('', 'nice', 'serious')
        self.assertEqual(len(keywords), len(uniquekeywords))
        for index, keyword in enumerate(keywords):
            self.assertEqual(uniquekeywords[index], keyword)

    def disabled_testSimpleTraversal(self):
        results = self.repository.restrictedTraverse('keywords/nice/queryImageRepository')
        print results
        self.assertEqual(len(results), 1)

    def disabled_testSimplePublish(self):
        self.setRoles(['Manager'])
        self.portal.portal_workflow.doActionFor(self.repository, 'publish')
        for image in images:
            self.portal.portal_workflow.doActionFor(getattr(self.repository,image['id']), 'publish')        
        response = self.publish(self.repositorypath + '/keywords/nice/queryImageRepository')
        print response
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Type'), 'text/html') # Our main_template doesn't set charset
        #print response


class TestBatchTagging(ImageRepositoryTestCase.ImageRepositoryTestCase):

    def afterSetUp(self):
        self.repository = _createObjectByType('ImageRepository', self.portal, 'repository')
        self.repository.at_post_create_script()
        for image in images:
            _createObjectByType('Image', self.repository, image['id'], image=loadImage(image['file']))

    def testBatchAdding(self):
        base_bath = "/".join(self.repository.getPhysicalPath())
        self.repository.imagerepository_addKeywords(
                paths=[base_bath+'/blue',base_bath+'/green'],
                subject_keywords=['primary']
        )
        repository = self.repository.restrictedTraverse('@@image_repository_view')
        results = self.portal.portal_catalog(portal_type='Image')
        uniquekeywords = repository.getUniqueKeywordsFromResults(results)
        keywords = (('primary',2),)
        self.assertEqual(len(keywords),len(uniquekeywords))
        for keyword in keywords:
            self.failUnless(uniquekeywords.has_key(keyword[0]))
            self.assertEqual(uniquekeywords[keyword[0]], keyword[1])

    def testBatchAddingToExisting(self):
        base_bath = "/".join(self.repository.getPhysicalPath())
        self.repository.imagerepository_addKeywords(
                paths=[base_bath+'/blue',base_bath+'/green'],
                subject_keywords=['primary']
        )
        repository = self.repository.restrictedTraverse('@@image_repository_view')
        results = self.portal.portal_catalog(portal_type='Image')
        uniquekeywords = repository.getUniqueKeywordsFromResults(results)
        keywords = (('primary',2),)
        self.assertEqual(len(keywords),len(uniquekeywords))
        for keyword in keywords:
            self.failUnless(uniquekeywords.has_key(keyword[0]))
            self.assertEqual(uniquekeywords[keyword[0]], keyword[1])
        self.repository.imagerepository_addKeywords(
                paths=[base_bath+'/blue',base_bath+'/purple'],
                subject_keywords=['serious']
        )
        repository = self.repository.restrictedTraverse('@@image_repository_view')
        results = self.portal.portal_catalog(portal_type='Image')
        uniquekeywords = repository.getUniqueKeywordsFromResults(results)
        keywords = (('primary',2),('serious',2))
        self.assertEqual(len(keywords),len(uniquekeywords))
        for keyword in keywords:
            self.failUnless(uniquekeywords.has_key(keyword[0]))
            self.assertEqual(uniquekeywords[keyword[0]], keyword[1])


class TestMakeImageRepositoryQuery(ImageRepositoryTestCase.ImageRepositoryTestCase):

    def afterSetUp(self):
        self.repository = _createObjectByType('ImageRepository', self.portal, 'repository')
        self.repository.at_post_create_script()

    def testAddingKeywords(self):
        repository = self.repository.restrictedTraverse('@@image_repository_view')
        form = {'keywords':['foo']}
        query_str = repository.makeImageRepositoryQuery(
            data=form,
            add={'keywords':['bar']}
        )
        expected = "keywords:list=foo&keywords:list=bar"
        self.assertEqual(query_str, expected)

    def testRemoveKeywords(self):
        repository = self.repository.restrictedTraverse('@@image_repository_view')
        form = {'keywords':['foo','bar']}
        query_str = repository.makeImageRepositoryQuery(
            data=form,
            omit={'keywords':['bar']}
        )
        expected = "keywords:list=foo"
        self.assertEqual(query_str, expected)
        query_str = repository.makeImageRepositoryQuery(
            data=form,
            omit={'keywords':['foo']}
        )
        expected = "keywords:list=bar"
        self.assertEqual(query_str, expected)

    def testAddRemoveKeywords(self):
        repository = self.repository.restrictedTraverse('@@image_repository_view')
        form = {'keywords':['foo','bar']}
        query_str = repository.makeImageRepositoryQuery(
            data=form,
            add={'keywords':['ugh']},
            omit={'keywords':['bar']}
        )
        expected = "keywords:list=foo&keywords:list=ugh"
        self.assertEqual(query_str, expected)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImageRepository))
    suite.addTest(makeSuite(TestBatchTagging))
    suite.addTest(makeSuite(TestMakeImageRepositoryQuery))
    return suite

if __name__ == '__main__':
    import unittest
    unittest.main()
