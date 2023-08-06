from BTrees.OOBTree import OOBTree
from Acquisition import aq_acquire

from zope.interface import implements
from zope.component import adapts, queryMultiAdapter
from zope.event import notify
from zope.publisher.interfaces.http import IHTTPRequest
from zope.annotation.interfaces import IAnnotatable, IAnnotations
from OFS.interfaces import ITraversable
from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import safe_unicode

from raptus.multilanguagefields.interfaces import IMultilanguageField
from raptus.multilanguageurls.interfaces import IMultilanguageURLHandler, MultilanguageIDModifiedEvent

ANNOTATIONS_KEY = 'raptus.multilanguageurls.mapping'


class MultilanguageURLHandler(object):
    implements(IMultilanguageURLHandler)
    adapts(IAnnotatable, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        annotations = IAnnotations(context)
        if not ANNOTATIONS_KEY in annotations:
            annotations[ANNOTATIONS_KEY] = OOBTree()
        self.storage = annotations[ANNOTATIONS_KEY]

    def dispatchEvent(self, id):
        notify(MultilanguageIDModifiedEvent(self.context[id]))

    def set_translated_id(self, id, translated, lang):
        """ Sets the translated ID for the given language and ID
        """
        id, translated = safe_unicode(id), safe_unicode(translated)
        if not id in self.context:
            return
        if not lang in self.storage:
            self.storage[lang] = OOBTree()
        if not 'index' in self.storage:
            self.storage['index'] = OOBTree()
        if not id == translated and not id == self.get_actual_id(translated) and not self.check_id(translated):
            obj = self.context[id]
            translated = obj._findUniqueId(translated)
            if translated is None:
                return
        langs = self.get_langs(self.storage[lang][id])
        if len(langs) == 1 and langs[0] == lang and self.storage[lang][id] in self.storage['index']:
            del self.storage['index'][self.storage[lang][id]]
        self.storage[lang][id] = translated
        self.storage['index'][translated] = id
        self.dispatchEvent(id)

    def remove_translated_ids(self, id):
        """ Removes all registered translated ids for the given ID
        """
        id = safe_unicode(id)
        for lang in self.storage:
            if not lang == 'index' and id in self.storage[lang]:
                translated = self.storage[lang][id]
                if 'index' in self.storage and translated in self.storage['index']:
                    del self.storage['index'][translated]
                del self.storage[lang][id]
        self.dispatchEvent(id)

    def get_translated_ids(self, id):
        """ Iterator of lang, ID pairs of all available translated IDs for the given ID
        """
        id = safe_unicode(id)
        if id in self.context:
            for lang in self.storage:
                if not lang == 'index' and id in self.storage[lang]:
                    yield lang, self.storage[lang][id]

    def get_translated_id(self, id, lang, event=True):
        """ Returns a translated ID of the object with the given ID and in the given language
        """
        id = safe_unicode(id)
        if not id in self.context:
            return id
        if not lang in self.storage:
            self.storage[lang] = OOBTree()
        if not id in self.storage[lang]:
            field = None
            try:
                obj = self.context[id]
                field = obj.Schema()['title']
                if not IMultilanguageField.providedBy(field):
                    return id

                field.setLanguage(lang)
                new_id = obj.generateNewId()
                field.resetLanguage()

                if new_id is None:
                    return id
                if (not 'index' in self.storage or
                    not new_id in self.storage['index'] or
                    not self.storage['index'][new_id] == id) and not new_id == id:
                    invalid_id = False
                    check_id = getattr(obj, 'check_id', None)
                    if check_id is not None:
                        invalid_id = check_id(new_id, required=1)

                    # If check_id told us no, or if it was not found, make sure we have an
                    # id unique in the parent folder.
                    if invalid_id:
                        unique_id = obj._findUniqueId(new_id)
                        if unique_id is not None:
                            if check_id is None or check_id(new_id, required=1):
                                new_id = unique_id
                                invalid_id = False

                    if invalid_id:
                        return id

                new_id = safe_unicode(new_id)
                self.storage[lang][id] = new_id
                if not 'index' in self.storage:
                    self.storage['index'] = OOBTree()
                self.storage['index'][new_id] = id
                if event:
                    self.dispatchEvent(id)
            except ConflictError, e:
                if field is not None and IMultilanguageField.providedBy(field):
                    field.resetLanguage()
                raise e
            except:
                if field is not None and IMultilanguageField.providedBy(field):
                    field.resetLanguage()
                return id
        return self.storage[lang][id]

    def get_actual_id(self, translated):
        """ Returns the actual ID of the object linked with the given translated ID, None otherwise
        """
        translated = safe_unicode(translated)
        if 'index' in self.storage and translated in self.storage['index']:
            return self.storage['index'][translated]
        return None

    def get_object(self, id):
        """ Returns the object having the given translated ID if available, None otherwise
        """
        id = safe_unicode(id)
        if not 'index' in self.storage:
            self.storage['index'] = OOBTree()
        if id in self.storage['index']:
            return self.context[self.storage['index'][id]]
        return None

    def get_langs(self, id):
        """ Returns the languages of the given translated ID if available
        """
        id = safe_unicode(id)
        langs = []
        for lang in self.storage.keys():
            if not lang == 'index' and id in self.storage[lang].values():
                langs.append(lang)
        return langs

    def check_id(self, id):
        """ Whether the given ID is not already in use
        """
        id = safe_unicode(id)
        return not 'index' in self.storage or not id in self.storage['index']


def update_translated_ids(obj, event):
    try:
        request = aq_acquire(obj, 'REQUEST')
    except:
        return
    handler = queryMultiAdapter((event.newParent, request), interface=IMultilanguageURLHandler)
    old_handler = queryMultiAdapter((event.oldParent, request), interface=IMultilanguageURLHandler)
    if handler is not None and old_handler is not None:
        for lang, id in old_handler.get_translated_ids(event.oldName):
            handler.set_translated_id(event.newName, id, lang)
    if not event.newParent is event.oldParent and old_handler is not None:
        old_handler.remove_translated_ids(event.oldName)
