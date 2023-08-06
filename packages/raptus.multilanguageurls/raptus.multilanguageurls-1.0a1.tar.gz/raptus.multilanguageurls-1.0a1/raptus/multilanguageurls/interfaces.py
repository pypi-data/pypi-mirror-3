from zope import interface
from zope.component.interfaces import IObjectEvent, ObjectEvent


class IMultilanguageIDModifiedEvent(IObjectEvent):
    """ An Event dispatched if one or more translated IDs of an
        object changed
    """


class MultilanguageIDModifiedEvent(ObjectEvent):
    """ An Event dispatched if one or more translated IDs of an
        object changed
    """
    interface.implements(IMultilanguageIDModifiedEvent)


class IMultilanguageURLHandler(interface.Interface):
    """ Manages ID translations of containers
    """

    def set_translated_id(id, translated, lang):
        """ Sets the translated ID for the given language and ID
        """

    def remove_translated_ids(id):
        """ Removes all registered translated IDs for the given ID
        """

    def get_translated_ids(id):
        """ Iterator of lang, ID pairs of all available translated IDs for the given ID
        """

    def get_translated_id(id, lang, event=True):
        """ Returns a translated ID of the given object and in the given language
        """

    def get_actual_id(translated):
        """ Returns the actual ID of the object linked with the given translated ID, None otherwise
        """

    def get_object(id):
        """ Returns the object having the given translated ID if available, None otherwise
        """

    def get_langs(id):
        """ Returns the languages of the given translated ID if available
        """

    def check_id(self, id):
        """ Whether the given ID is not already in use
        """
