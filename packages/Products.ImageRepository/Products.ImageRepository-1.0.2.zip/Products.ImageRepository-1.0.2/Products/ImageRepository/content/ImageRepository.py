from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import registerType
from Products.ImageRepository.interfaces import IImageRepository
from Products.ImageRepository.config import PROJECTNAME

from Products.ATContentTypes.atct import ATBTreeFolderSchema
from Products.ATContentTypes.atct import ATCTBTreeFolder
from Products.ATContentTypes.interfaces import IATBTreeFolder

from Products.CMFPlone.interfaces.Translatable import ITranslatable


def flatten(ltypes=(list, tuple), *args):
    for arg in args:
        if isinstance(arg, ltypes):
            for i in arg:
                for l in flatten(i):
                    yield l
        else:
            yield arg

def updateInterfaces(*args):
    return tuple(x for x in flatten(args) if x is not ITranslatable)


ImageRepositorySchema = ATBTreeFolderSchema.copy()

class ImageRepository(ATCTBTreeFolder):
    """A repository to store images."""
    implements(IImageRepository)

    schema = ImageRepositorySchema

    security = ClassSecurityInfo()

    __implements__ = updateInterfaces(ATCTBTreeFolder.__implements__, IATBTreeFolder)

registerType(ImageRepository, PROJECTNAME)
