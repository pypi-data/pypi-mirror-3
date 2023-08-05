from zope.interface import implements
from zope.component import queryAdapter

from Products.ImageRepository.interfaces import IThumbnail


class BrainThumbnail(object):

    implements(IThumbnail)

    def __init__(self, context):
        self.context = context

    def html_tag(self, size='thumb'):
        obj = self.context.getObject()
        adapter = queryAdapter(obj, IThumbnail)
        if adapter is not None:
            return adapter.html_tag(size)
        else:
            return None


class ATImageThumbnail(object):

    implements(IThumbnail)

    def __init__(self, context):
        self.context = context

    def html_tag(self, size='thumb'):
        return self.context.tag(scale=size, title=self.context.Description())
