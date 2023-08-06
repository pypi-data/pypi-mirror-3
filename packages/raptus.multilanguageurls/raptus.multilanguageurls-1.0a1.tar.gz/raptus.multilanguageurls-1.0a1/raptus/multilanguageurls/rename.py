from Acquisition import aq_parent, aq_inner, aq_acquire
from AccessControl.Permissions import copy_or_move

from zope import interface
from zope import schema
from zope.component import queryMultiAdapter, adapts
from zope.formlib.form import EditForm, FormFields, action, applyData
from zope.schema.interfaces import ValidationError
from zope.app.form.interfaces import WidgetInputError
from plone.app.imaging.interfaces import IBaseObject

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent, DeleteObjects
from Products.CMFPlone import PloneMessageFactory as _p
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage

from raptus.multilanguagefields.interfaces import IMultilanguageField
from raptus.multilanguageurls.interfaces import IMultilanguageURLHandler


class InvalidIDError(ValidationError):
    def __init__(self, doc):
        self.__doc__ = doc
    def doc(self):
        return self.__doc__


class IRenameForm(interface.Interface):
    """ The rename form
    """

    id = schema.TextLine(
        title=_p(u'label_new_short_name', default=u'New Short Name'),
        description=_p(u'help_short_name_url', default=u'Short name is the part that shows up in the URL of the item.'),
        required=True
    )

    title = schema.TextLine(
        title=_p(u'label_new_title', u'New Title'),
        required=True
    )


class RenameFormAdapter(object):
    interface.implements(IRenameForm)
    adapts(IBaseObject)

    def __init__(self, context):
        self.context = context
        self.languages = getToolByName(context, 'portal_languages').getSupportedLanguages()
        self.handler = queryMultiAdapter((aq_parent(aq_inner(context)), aq_acquire(context, 'REQUEST')), interface=IMultilanguageURLHandler)

    def __setattr__(self, name, value):
        if name in ('languages', 'context', 'handler',):
            object.__setattr__(self, name, value)
        elif name == 'id':
            self.context.setId(value)
        elif name == 'title':
            self.context.setTitle(value)
        elif name in self.languages:
            self.handler.set_translated_id(self.id, value, name)
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name in ('languages', 'context', 'handler',):
            return object.__getattr__(self, name)
        if name == 'id':
            return self.context.getId()
        if name == 'title':
            return self.context.Title()
        if name in self.languages:
            return self.handler.get_translated_id(self.id, name)
        return object.__getattr__(self, name)


class RenameForm(EditForm):

    label = _p(u'heading_rename_item', default=u'Rename item')
    description = _p(u'description_rename_item',
                    default=u'Each item has a Short Name and a Title, which you can change '
                             'by entering the new details below.')

    def __init__(self, context, request):
        super(RenameForm, self).__init__(context, request)
        for name, value in self.request.form.items():
            self.request.form[name] = safe_unicode(value)
        self.form_fields = FormFields(IRenameForm)
        self.form_name = '%s (%s)' % (self.context.Title(), self.context.getId())
        mtool = getToolByName(self.context, 'portal_membership')
        title = self.context.Schema()['title']
        self.id = self.context.getId()
        self.languages = {}
        if (IMultilanguageField.providedBy(title) or
            not mtool.checkPermission(DeleteObjects, self.context) or
            not mtool.checkPermission(copy_or_move, self.context)):
            self.form_fields = self.form_fields.omit('id')
        if (IMultilanguageField.providedBy(title) or
            not mtool.checkPermission(ModifyPortalContent, self.context)):
            self.form_fields = self.form_fields.omit('title')
        if IMultilanguageField.providedBy(title):
            self.handler = queryMultiAdapter((aq_parent(aq_inner(self.context)), self.request), interface=IMultilanguageURLHandler)
            for lang in title.getAvailableLanguages(self.context):
                self.languages[lang['name']] = lang['title']
                self.form_fields = self.form_fields + FormFields(
                    schema.TextLine(
                        __name__=lang['name'],
                        title=lang['title'],
                        default=self.handler.get_translated_id(self.id, lang['name']),
                        required=True
                    )
                )
                self.form_fields[lang['name']].interface = IRenameForm

    def validate(self, action, data):
        errors = super(RenameForm, self).validate(action, data)
        for field in self.form_fields:
            name = field.field.getName()
            if name == 'title':
                continue
            value = data.get(name, u'')
            check_id = getattr(self.context, 'check_id', None)
            if ((name == 'id' and not value == self.id) or
                (name in self.languages.keys() and not value == self.handler.get_translated_id(self.id, name) and
                 not value == self.id and not self.id == self.handler.get_actual_id(value)) and
                check_id is not None):
                error = check_id(str(value), required=1)
                if error:
                    widget = self.widgets[name]
                    widget._error = WidgetInputError(widget.name, widget.label, InvalidIDError(error))
                    errors.append(widget._error)
        return errors

    @action(_p(u'label_rename_all', default=u'Rename All'), name=u'rename')
    def handle_rename_action(self, action, data):
        context = aq_inner(self.context)
        oldid = context.getId()
        oldtranslatedids = self.handler.get_translated_ids(oldid)
        descriptions = applyData(context, self.form_fields, data, self.adapters)
        statusmessage = IStatusMessage(self.request)
        if descriptions:
            statusmessage.addStatusMessage(_p(u'Changes saved.'), u'success');
        else:
            statusmessage.addStatusMessage(_p(u'No changes made.'));
        self.request.RESPONSE.redirect(context.absolute_url())
