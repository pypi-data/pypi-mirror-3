from zope.i18nmessageid import MessageFactory

from Products.CMFCore.utils import ContentInit

from Products.Archetypes.public import listTypes
from Products.Archetypes.public import process_types

from Products.ImageRepository import config
from Products.ImageRepository import permissions

ImageRepositoryMessageFactory = MessageFactory('Products.ImageRepository')

def initialize(context):

    from Products.ImageRepository import content

    content_types, constructors, ftis = process_types(
        listTypes(config.PROJECTNAME), config.PROJECTNAME)

    ContentInit(
        config.PROJECTNAME + ' Content',
        content_types = content_types,
        permission = permissions.AddImageRepositoryContent,
        extra_constructors = constructors,
    ).initialize(context)
