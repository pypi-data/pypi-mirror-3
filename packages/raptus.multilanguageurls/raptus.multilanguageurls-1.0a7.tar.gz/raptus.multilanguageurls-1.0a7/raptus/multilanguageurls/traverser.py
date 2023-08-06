from zope.interface import implements
from zope.component import adapts
from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.publisher.interfaces.http import IHTTPRequest
from zope.annotation.interfaces import IAnnotatable
from plone.app.imaging.interfaces import IBaseObject
from plone.app.imaging.traverse import ImageTraverser

from Products.CMFCore.utils import getToolByName
from ZPublisher.BaseRequest import DefaultPublishTraverse

from raptus.multilanguageurls.interfaces import IMultilanguageURLHandler


class MultilanguageTraverse(object):
    implements(IPublishTraverse)
    adapts(IAnnotatable, IHTTPRequest)

    def __init__(self,context,request):
        self.context = context
        self.request = request
        self.default_traverse = DefaultPublishTraverse(context, request)
        self.handler = IMultilanguageURLHandler(context, None)

    def publishTraverse(self, request, name):
        if self.handler is not None:
            ob = self.handler.get_object(name)
            if ob is not None:
                langs = self.handler.get_langs(name)
                if len(langs) == 1:
                    try:
                        portal_languages = getToolByName(self.context, 'portal_languages')
                        portal_languages.REQUEST.set_lazy('set_language', lambda: langs[0])
                        portal_languages.setLanguageBindings()
                    except:
                        pass
                return ob
        try:
            return self.default_traverse.publishTraverse(request, name)
        except NotFound:
            pass
        except KeyError:
            pass
        except AttributeError:
            pass
        raise NotFound(self.context, name, self.request)


class MultilanguageImageTraverse(MultilanguageTraverse):
    implements(IPublishTraverse)
    adapts(IBaseObject, IHTTPRequest)

    def publishTraverse(self, request, name):
        try:
            return super(MultilanguageImageTraverse, self).publishTraverse(request, name)
        except NotFound:
            pass
        return ImageTraverser(self.context, self.request).publishTraverse(request, name)
