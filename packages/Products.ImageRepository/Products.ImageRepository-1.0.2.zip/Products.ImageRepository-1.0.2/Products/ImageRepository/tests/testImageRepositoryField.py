import unittest
import pprint

from zope.interface import implements
from Products.ImageRepository.field import IScaledImage

class MockInstance:
    implements(IScaledImage)
    
    def getRefs(self, relationship):
        self.used_rel = relationship
        return [self]
    
    def getFileSize(self):
        return 12345
    
    def getContentType(self):
        return 'image/jpeg'
    
    def getFilename(self):
        return 'foobar.jpg'
    
    def getAvailableSizes(self):
        return dict(foo=(10, 10), spam=(20, 20))
    
    def getSize(self, scale=None, **kwargs):
        if scale is None:
            return (100, 100)
        return (10, 10)
    
    def getScale(self, scale=None, **kwargs):
        return scale
    
    def tag(self, scale=None, height=None, width=None, alt=None,
            css_class=None, title=None, **kwargs):
        return pprint.pformat((scale, height, width, alt, css_class,
                               title, kwargs))

class ImageRepositoryFieldTests(unittest.TestCase):
    def setUp(self):
        from Products.ImageRepository.field import ImageRepositoryField
        self.instance = MockInstance()
        self.field = ImageRepositoryField('monty')
        
    def testRelationshipName(self):
        self.assertEqual(self.field.relationship, 'imagerepositoryfield-monty')
        
    def testGetScaleName(self):
        self.assertEqual(self.field.getScaleName('foo'), 'monty_foo')
        
    def testGetFileSize(self):
        self.assertEqual(self.field.getFileSize(self.instance),
                         self.instance.getFileSize())
        
    def testGetContentType(self):
        self.assertEqual(self.field.getContentType(self.instance),
                         self.instance.getContentType())
        
    def testGetFilename(self):
        self.assertEqual(self.field.getFilename(self.instance),
                         self.instance.getFilename())
        
    def testGetAvailableSizes(self):
        self.assertEqual(self.field.getAvailableSizes(self.instance),
                         self.instance.getAvailableSizes())
        
    def testGetSize(self):
        self.assertEqual(self.field.getSize(self.instance),
                         self.instance.getSize())
        self.assertEqual(self.field.getSize(self.instance, 'foo'),
                         self.instance.getSize('foo'))
        
    def testGetScale(self):
        self.assertEqual(self.field.getScale(self.instance),
                         self.instance.getScale())
        self.assertEqual(self.field.getScale(self.instance, 'foo'),
                         self.instance.getScale('foo'))
        
    def testTag(self):
        self.assertEqual(self.field.tag(self.instance),
                         self.instance.tag())
        self.assertEqual(self.field.tag(self.instance, width=100),
                         self.instance.tag(width=100))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImageRepositoryFieldTests))
    return suite

if __name__ == '__main__':
    unittest.main()
