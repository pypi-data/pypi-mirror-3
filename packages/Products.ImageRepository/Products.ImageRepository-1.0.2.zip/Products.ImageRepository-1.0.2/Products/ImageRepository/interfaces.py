# Zope3 imports
from zope.interface import Interface


class IImageRepository(Interface):
    """An image repository.
    """


class IImageRepositoryView(Interface):
    """A view for an image repository.
    """

    def getImageRepositoryURL():
        """
        """

    def getUniqueKeywordsFromResults(results):
        """
        """
        
    def getSearchKeywordsFromResults(results):
        """
        """

    def queryImageRepository(query=None, REQUEST=None):
        """
        """

    def makeImageRepositoryQuery(data=None, add=None, omit=None):
        """
        """

    def thumbnail_tag(obj, size=128):
        """
        """


class IImageRepositoryAdminView(Interface):
    """A view with administration methods."""

    def registerInKupu():
        """Registers the ImageRepository in Kupu."""


class IThumbnail(Interface):
    """Marker interface for objects which provide thumbnails."""

    def html_tag(size='thumb'):
        """Return a HTML string that is the tag for rendering the thumbnail.
        """

