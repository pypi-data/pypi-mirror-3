"""ImageRepository field.

Use this instead of a regular image field to store images in the repository
instead of on the object itself. This allows users to re-use repository
images.

"""
from zope.component import adapts
from zope.interface import Interface, implements
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute

from Products.Archetypes.Field import ReferenceField
from Products.Archetypes.Registry import registerField
from Products.ATContentTypes.interface import IATImage
from Products.CMFCore.permissions import View

from widget import ImageRepositoryWidget

class IScaledImage(Interface):
    """A scaled image, such as an ATContentTypes.image object"""
    
    def getFileSize():
        """The filesize in bytes of the image"""
    
    def getContentType():
        """The mime-type of the image"""
        
    def getFilename():
        """Return the filename of the image"""
    
    def getAvailableSizes():
        """Return a dict of scalename -> (width, height) entries"""
        
    def getSize(scale=None):
        """Return a tuple of (width, height) for a given scale name"""
        
    def getScale(scale=None, **kwargs):
        """Return the image for the given scale"""
        
    def tag(scale=None, height=None, width=None, alt=None, css_class=None,
            title=None, **kwargs):
        """Return a HTML <img> tag for given scale, using the OFS.Image API"""


class ATScalableImageAdapter:
    implements(IScaledImage)
    adapts(IATImage)
    
    def __init__(self, context):
        self.context = context
        
    def getFileSize(self):
        return self.context.get_size()
        
    def getContentType(self):
        return self.context.getContentType()
    
    def getFilename(self):
        field = self.context.getField('image')
        return field.getFilename(self.context)
        
    def getAvailableSizes(self):
        field = self.context.getField('image')
        return field.getAvailableSizes(self.context)
    
    def getSize(self, scale=None):
        return self.context.getSize(scale)
    
    def getScale(self, scale=None, **kwargs):
        field = self.context.getField('image')
        return field.getScale(self.context, scale, **kwargs)
    
    def tag(self, scale=None, height=None, width=None, alt=None,
            css_class=None, title=None, **kwargs):
        return self.context.tag(scale=scale, height=height, width=width,
                                alt=alt, css_class=css_class, title=title,
                                **kwargs)
    

class ImageRepositoryField(ReferenceField):
    """A field that stores references to imagerepository images
    
    It otherwise emulates the read interface of the Image field, so
    information like getScale and getAvailableSizes is present.
    
    """
    _properties = ReferenceField._properties.copy()
    del _properties['relationship']
    _properties.update(dict(
        type='imagerepository',
        widget=ImageRepositoryWidget,
    ))
    
    security = ClassSecurityInfo()
    
    def relationship(self):
        """Create a field-name-based relationship qualifier"""
        return 'imagerepositoryfield-' + self.getName()
    relationship = ComputedAttribute(relationship)
    
    security.declareProtected(View, 'getScaleName')
    def getScaleName(self, scale=None):
        """Get the full name of the attribute for the scale"""
        if scale:
            return self.getName() + "_" + scale
        else:
            return ''
        
    def _getScalableImage(self, instance):
        """Return the image, adapted to IScalableImage"""
        image = self.get(instance)
        try:
            return IScaledImage(image)
        except TypeError:
            return None
    
    security.declarePrivate('getImageSize')
    def getFileSize(self, instance):
        """The size in bytes of the image
        
        Delegated to the referenced image.
        
        """
        image = self._getScalableImage(instance)
        if not image:
            return 0
        return image.getFileSize()
    
    security.declarePrivate('getFilename')
    def getFilename(self, instance, **kwargs):
        """The original filename of the image
        
        Delegated to the referenced image.
        
        """
        image = self._getScalableImage(instance)
        if not image:
            return ''
        return image.getFilename()
    
    security.declarePublic('getContentType')
    def getContentType(self, instance, **kwargs):
        """The content type of the image
        
        Delegated to the referenced image.
        
        """
        image = self._getScalableImage(instance)
        if not image:
            return 'text/plain'
        return image.getContentType()
    
    security.declareProtected(View, 'getAvailableSizes')
    def getAvailableSizes(self, instance):
        """Get sizes

        Delegated to referenced image.
        
        """
        image = self._getScalableImage(instance)
        if not image:
            return {}
        return image.getAvailableSizes()
    
    security.declareProtected(View, 'getSize')
    def getSize(self, instance, scale=None):
        """get size of scale or original
        
        Delegated to referenced image.
        
        """
        image = self._getScalableImage(instance)
        if not image:
            return 0, 0
        return image.getSize(scale)

    security.declareProtected(View, 'getScale')
    def getScale(self, instance, scale=None, **kwargs):
        """Get scale by name or original
        
        Delegated to referenced image.
        
        """
        image = self._getScalableImage(instance)
        if not image:
            return None
        return image.getScale(scale, **kwargs)

    security.declareProtected(View, 'tag')
    def tag(self, instance, scale=None, height=None, width=None, alt=None,
            css_class=None, title=None, **kwargs):
        """Create a tag including scale
        
        Delegated to referenced image.
        
        """
        image = self._getScalableImage(instance)
        if not image:
            return None
        return image.tag(scale, height, width, alt, css_class, title, **kwargs)
    
registerField(
    ImageRepositoryField, title='Image Repository image',
    description='Store a reference to an image from a image repository')
