from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree

from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.unauthorized import Unauthorized
from AccessControl.ZopeGuards import guarded_getattr
from Acquisition import aq_inner, aq_parent, aq_acquire, aq_base
from Acquisition.interfaces import IAcquirer
from zExceptions import NotFound
from OFS.Traversable import path2url, _marker
from OFS.interfaces import ITraversable
from ZODB.POSException import ConflictError

from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.interfaces import IPloneSiteRoot

from zope.interface import Interface
from zope.traversing.interfaces import TraversalError
from zope.traversing.namespace import namespaceLookup
from zope.traversing.namespace import nsParse
from zope.component import queryMultiAdapter

from raptus.multilanguageurls.interfaces import IMultilanguageURLHandler


# Patching OFS.Traversable.Traversable

def _getTranslatedPhysicalPath(obj, lang=None, event=True):
    if not hasattr(obj, 'getId'):
        return ()
    id = obj.getId()
    p = aq_parent(aq_inner(obj))
    handler = IMultilanguageURLHandler(p, None)
    if handler is not None:
        if lang is None:
            lang = getToolByName(obj, 'portal_languages').getPreferredLanguage()
        id = handler.get_translated_id(id, lang, event)

    path = (id,)

    if p is not None:
        path = _getTranslatedPhysicalPath(p, lang, event) + path

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

def unrestrictedTraverse(self, path, default=_marker, restricted=False):
    """ Need to patch traversing to respect multilanguage urls
        
        (This is a direct copy from OFS.Traversable.Traversable, with only
        the marked parts adjusted)
    """
    from webdav.NullResource import NullResource
    if not path:
        return self

    if isinstance(path, str):
        # Unicode paths are not allowed
        path = path.split('/')
    else:
        path = list(path)

    REQUEST = {'TraversalRequestNameStack': path}
    path.reverse()
    path_pop = path.pop

    if len(path) > 1 and not path[0]:
        # Remove trailing slash
        path_pop(0)

    if restricted:
        validate = getSecurityManager().validate

    if not path[-1]:
        # If the path starts with an empty string, go to the root first.
        path_pop()
        obj = self.getPhysicalRoot()
        if restricted:
            validate(None, None, None, obj) # may raise Unauthorized
    else:
        obj = self

    resource = _marker
    try:
        while path:
            name = path_pop()

            # Starting patch (looking up the possible actual name if the name is a
            # translated one)
            handler = IMultilanguageURLHandler(obj, None)
            if handler is not None:
                actual = handler.get_actual_id(name)
                if actual is not None:
                    name = str(actual)
            # End of patch

            __traceback_info__ = path, name

            if name[0] == '_':
                # Never allowed in a URL.
                raise NotFound, name

            if name == '..':
                next = aq_parent(obj)
                if next is not None:
                    if restricted and not validate(obj, obj, name, next):
                        raise Unauthorized(name)
                    obj = next
                    continue

            bobo_traverse = getattr(obj, '__bobo_traverse__', None)
            try:
                if name and name[:1] in '@+' and name != '+' and nsParse(name)[1]:
                    # Process URI segment parameters.
                    ns, nm = nsParse(name)
                    try:
                        next = namespaceLookup(
                            ns, nm, obj, aq_acquire(self, 'REQUEST'))
                        if IAcquirer.providedBy(next):
                            next = next.__of__(obj)
                        if restricted and not validate(
                            obj, obj, name, next):
                            raise Unauthorized(name)
                    except TraversalError:
                        raise AttributeError(name)

                elif bobo_traverse is not None:
                    next = bobo_traverse(REQUEST, name)
                    if restricted:
                        if aq_base(next) is not next:
                            # The object is wrapped, so the acquisition
                            # context is the container.
                            container = aq_parent(aq_inner(next))
                        elif getattr(next, 'im_self', None) is not None:
                            # Bound method, the bound instance
                            # is the container
                            container = next.im_self
                        elif getattr(aq_base(obj), name, _marker) is next:
                            # Unwrapped direct attribute of the object so
                            # object is the container
                            container = obj
                        else:
                            # Can't determine container
                            container = None
                        # If next is a simple unwrapped property, its
                        # parentage is indeterminate, but it may have
                        # been acquired safely. In this case validate
                        # will raise an error, and we can explicitly
                        # check that our value was acquired safely.
                        try:
                            ok = validate(obj, container, name, next)
                        except Unauthorized:
                            ok = False
                        if not ok:
                            if (container is not None or
                                guarded_getattr(obj, name, _marker)
                                    is not next):
                                raise Unauthorized(name)
                else:
                    if getattr(aq_base(obj), name, _marker) is not _marker:
                        if restricted:
                            next = guarded_getattr(obj, name)
                        else:
                            next = getattr(obj, name)
                    else:
                        try:
                            next = obj[name]
                            # The item lookup may return a NullResource,
                            # if this is the case we save it and return it
                            # if all other lookups fail.
                            if isinstance(next, NullResource):
                                resource = next
                                raise KeyError(name)
                        except AttributeError:
                            # Raise NotFound for easier debugging
                            # instead of AttributeError: __getitem__
                            raise NotFound(name)
                        if restricted and not validate(
                            obj, obj, None, next):
                            raise Unauthorized(name)

            except (AttributeError, NotFound, KeyError), e:
                # Try to look for a view
                next = queryMultiAdapter((obj, aq_acquire(self, 'REQUEST')),
                                         Interface, name)

                if next is not None:
                    if IAcquirer.providedBy(next):
                        next = next.__of__(obj)
                    if restricted and not validate(obj, obj, name, next):
                        raise Unauthorized(name)
                elif bobo_traverse is not None:
                    # Attribute lookup should not be done after
                    # __bobo_traverse__:
                    raise e
                else:
                    # No view, try acquired attributes
                    try:
                        if restricted:
                            next = guarded_getattr(obj, name, _marker)
                        else:
                            next = getattr(obj, name, _marker)
                    except AttributeError:
                        raise e
                    if next is _marker:
                        # If we have a NullResource from earlier use it.
                        next = resource
                        if next is _marker:
                            # Nothing found re-raise error
                            raise e

            obj = next

        return obj

    except ConflictError:
        raise
    except:
        if default is not _marker:
            return default
        else:
            raise


# Patching OFS.ObjectManager.ObjectManager
from OFS.ObjectManager import ObjectManager

def checkValidId(self, id):
    handler = IMultilanguageURLHandler(self, None)
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
            self.translated_paths[lang][index] = str('/'.join(_getTranslatedPhysicalPath(object, lang, False)))
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
