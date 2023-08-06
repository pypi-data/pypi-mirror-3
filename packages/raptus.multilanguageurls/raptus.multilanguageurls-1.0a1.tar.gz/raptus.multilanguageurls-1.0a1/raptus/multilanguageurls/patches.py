from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree

from Acquisition import aq_inner, aq_parent, aq_acquire
from OFS.Traversable import path2url

from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.interfaces import IPloneSiteRoot

from zope.component import queryMultiAdapter

from raptus.multilanguageurls.interfaces import IMultilanguageURLHandler


# Patching OFS.Traversable.Traversable

def _getTranslatedPhysicalPath(obj, lang=None, request=None, event=True):
    if not hasattr(obj, 'getId'):
        return ()
    if request is None:
        try:
            request = aq_acquire(obj, 'REQUEST')
        except AttributeError:
            pass
    id = obj.getId()
    p = aq_parent(aq_inner(obj))
    if request is not None:
        handler = queryMultiAdapter((p, request), interface=IMultilanguageURLHandler)
        if handler is not None:
            if lang is None:
                lang = getToolByName(obj, 'portal_languages').getPreferredLanguage()
            id = handler.get_translated_id(id, lang, event)

    path = (id,)

    if p is not None:
        path = _getTranslatedPhysicalPath(p, lang, request, event) + path

    return path

def absolute_url(self, relative=0):
    if relative:
        return self.virtual_url_path()
    spp = _getTranslatedPhysicalPath(self)
    try:
        toUrl = aq_acquire(self, 'REQUEST').physicalPathToURL
    except AttributeError:
        return path2url(spp[1:])
    return toUrl(spp)

def absolute_url_path(self):
    spp = _getTranslatedPhysicalPath(self)
    try:
        toUrl = aq_acquire(self, 'REQUEST').physicalPathToURL
    except AttributeError:
        return path2url(spp) or '/'
    return toUrl(spp, relative=1) or '/'

def virtual_url_path(self):
    spp = _getTranslatedPhysicalPath(self)
    try:
        toVirt = aq_acquire(self, 'REQUEST').physicalPathToVirtualPath
    except AttributeError:
        return path2url(spp[1:])
    return path2url(toVirt(spp))


# Patching OFS.ObjectManager.ObjectManager
from OFS.ObjectManager import ObjectManager

def checkValidId(self, id):
    request = aq_acquire(self, 'REQUEST')
    handler = queryMultiAdapter((self, request), interface=IMultilanguageURLHandler)
    if handler is not None and not handler.check_id(id):
        raise KeyError('The given id %s is already in use' % id)
ObjectManager.checkValidId = checkValidId


# Patching Products.ZCatalog.Catalog.Catalog
from Products.ZCatalog.Catalog import Catalog

__old_catalogObject = Catalog.catalogObject

def catalogObject(self, object, uid, threshold=None, idxs=None,
                  update_metadata=1):
    total = __old_catalogObject(self, object, uid, threshold, idxs,
                                update_metadata)
    self.updateTanslatedPaths(object, uid)
    return total

def updateTanslatedPaths(self, object, uid):
    if ICatalogTool.providedBy(object):
        return
    try:
        request = aq_acquire(object, 'REQUEST')
    except:
        return
    if request is not None:
        if not hasattr(self, 'translated_paths'):
            self.translated_paths = OOBTree()
        index = self.uids.get(uid, None)
        if index is None:
            return
        langs = getToolByName(object, 'portal_languages').getSupportedLanguages()
        for lang in langs:
            if not lang in self.translated_paths:
                self.translated_paths[lang] = IOBTree()
            self.translated_paths[lang][index] = str('/'.join(_getTranslatedPhysicalPath(object, lang, request, False)))
Catalog.updateTanslatedPaths = updateTanslatedPaths

def update_translated_paths(obj, event):
    catalog = getToolByName(obj, 'portal_catalog')
    def updateTranslatedPaths(obj, path=None):
        if (base_hasattr(obj, 'indexObject') and
            safe_callable(obj.indexObject) and
            base_hasattr(obj, 'getPhysicalPath') and
            safe_callable(obj.getPhysicalPath)):
            try:
                catalog._catalog.updateTanslatedPaths(obj, '/'.join(obj.getPhysicalPath()))
            except:
                pass
    portal = aq_parent(aq_inner(catalog))
    updateTranslatedPaths(obj)
    portal.ZopeFindAndApply(obj, search_sub=True, apply_func=updateTranslatedPaths)

__old_uncatalogObject = Catalog.uncatalogObject

def uncatalogObject(self, uid):
    __old_uncatalogObject(self, uid)
    index = self.uids.get(uid, None)
    if index is None:
        return
    if not hasattr(self, 'translated_paths'):
        return
    for lang in self.translated_paths:
        if index in self.translated_paths[lang]:
            del self.translated_paths[lang][index]


# Patching Products.ZCatalog.CatalogBrains.AbstractCatalogBrain
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

__old_getURL = AbstractCatalogBrain.getURL

def getURL(self, relative=0):
    if not hasattr(self.aq_parent._catalog, 'translated_paths'):
        return __old_getURL(self, relative)
    lang = getToolByName(self.aq_parent, 'portal_languages').getPreferredLanguage()
    if (not lang in self.aq_parent._catalog.translated_paths or
        not self.data_record_id_ in self.aq_parent._catalog.translated_paths[lang]):
        return __old_getURL(self, relative)
    return self.REQUEST.physicalPathToURL(self.aq_parent._catalog.translated_paths[lang][self.data_record_id_], relative)
