from zope.interface import implements
from zope.component import adapter, queryMultiAdapter

from Products.Five import BrowserView

from Products.Archetypes.utils import DisplayList
from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from Products.ImageRepository import ImageRepositoryMessageFactory as _
from Products.ImageRepository.interfaces import IImageRepository
from Products.ImageRepository.interfaces import IImageRepositoryView
from Products.ImageRepository.interfaces import IImageRepositoryAdminView
from Products.ImageRepository.interfaces import IThumbnail

import urllib
from ZTUtils.Zope import complex_marshal


class ImageRepositoryView(BrowserView):

    implements(IImageRepositoryView)

    def getUniqueKeywordsFromResults(self, results):
        keywords = {}
        for item in results:
            subjects = item.Subject
            if subjects is not None:
                for keyword in subjects:
                    keywords[keyword] = keywords.get(keyword, 0) + 1
        return keywords

    def getSearchKeywordsFromResults(self, results):
        keywords = self.getUniqueKeywordsFromResults(results)
        results_len = len(results)
        for key, count in keywords.items():
            if count == results_len:
                del keywords[key]
        keywords = keywords.keys()
        keywords.sort()
        result = DisplayList()
        if len(keywords):
            result.add('', '[no keywords]', msgid='label_no_keywords')
        for item in keywords:
            result.add(item, item)
        return result

    def getImageRepositoryPath(self):
        return "/".join(self.context.getPhysicalPath())

    def getImageRepositoryURL(self):
        return self.context.absolute_url()

    def queryImageRepository(self, query=None, REQUEST=None):
        if REQUEST is None:
            request = self.context.REQUEST
        else:
            request = REQUEST
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        if query is None:
            query = {}
        portal_types = portal_catalog.uniqueValuesFor('portal_type')
        portal_types = [x for x in portal_types if x != 'ImageRepository']
        query['portal_type'] = portal_types
        query['path'] = self.getImageRepositoryPath()
        keywords = request.get('keywords', None)
        if keywords is not None:
            if keywords[0] == '':
                results = portal_catalog(query)
                return [x for x in results if x.Subject == ()]
            else:
                query['Subject'] = {'query':keywords, 'operator':'and'}
        return portal_catalog(query)

    def makeImageRepositoryQuery(self, data=None, add=None, omit=None):
        d = {}
        if data is not None:
            d.update(data)
        if add is not None:
            for key in add:
                if not d.has_key(key):
                    d[key] = add[key]
                else:
                    if isinstance(d[key], list):
                        d[key] = d[key] + add[key]
        if omit is not None:
            for key in omit:
                if d.has_key(key):
                    value = omit[key]
                    if not isinstance(value, list):
                        value = [value]
                    for v in value:
                        d[key] = [x for x in d[key] if x!=v]
        uq = urllib.quote
        qlist = complex_marshal(d.items())
        for i in range(len(qlist)):
            k, m, v = qlist[i]
            qlist[i] = '%s%s=%s' % (uq(k), m, uq(str(v)))

        return '&'.join(qlist)

    def thumbnail_tag(self, obj, size='thumb'):
        return IThumbnail(obj).html_tag(size)


class ImageRepositoryAdminView(BrowserView):

    implements(IImageRepositoryAdminView)

    def registerInKupu(self):
        """Registeres this repository as a library in Kupu."""
        request = self.request
        response = request.response
        kupuTool = getToolByName(self.context, 'kupu_library_tool', None)
        if kupuTool is not None:
            portal_url = getToolByName(self.context, 'portal_url')
            library_ids = [x['id'] for x in kupuTool._libraries]
            repository_path = self.context.getPhysicalPath()
            portal = portal_url.getPortalObject()
            portal_path = portal.getPhysicalPath()
            sub_path = repository_path[len(portal_path):]
            path = "/".join(sub_path)
            name = "-".join(sub_path)
            if name not in library_ids:
                kupuTool.addLibrary(name,
                                    'string:%s' % self.context.pretty_title_or_id(),
                                    'string:${portal_url}/%s/imagerepository_collection.xml' % path,
                                    'string:${portal_url}/%s/imagerepository_collection.xml' % path,
                                    'string:${portal_url}/imagerepository_icon.gif')
                message = _(u"Registered repository in Kupu.")
                IStatusMessage(request).addStatusMessage(message, type='info')
                response.redirect(self.context.absolute_url()+'/view')
        else:
            message = _("Kupu is not installed.")
            IStatusMessage(request).addStatusMessage(message, type='info')
            response.redirect(self.context.absolute_url()+'/view')


@adapter(IImageRepository, IObjectInitializedEvent)
def ImageRepositoryCreatedHandler(ob, event):
    view = queryMultiAdapter((ob, ob.REQUEST),
                             name='image_repository_admin_view')
    if view is not None:
        view.registerInKupu()
