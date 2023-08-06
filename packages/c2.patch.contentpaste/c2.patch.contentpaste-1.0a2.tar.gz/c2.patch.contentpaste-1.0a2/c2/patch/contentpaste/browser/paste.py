# coding: utf-8
from random import random
from DateTime import DateTime
from Acquisition import aq_inner, aq_parent
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter
from zope.interface import providedBy

from Products.CMFCore.utils import getToolByName
# from Products.CMFCore.utils import _checkPermission
from Products.Five import BrowserView
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.Archetypes.interfaces.field import IFileField
from Products.Archetypes.interfaces.field import ITextField
from plone.app.blob.interfaces import IBlobField

from c2.patch.contentpaste import ContentPasteMessageFactory as _

from zope.i18n import translate

# COPY_TARGET_SCHEMATAS = ['default',]
COPY_IGNORE_SCHEMATAS = ['dates', 'ownership', 'settings']
COPY_IGNORE_FIELDS = set(('id',))
ADDING_TITLE = _(u"copy_of_")

def _get_schemata_fields(obj, schemata):
    return obj.schema.getSchemataFields(schemata)

def _get_ignore_fields_in_schematas(obj):
    for schemata in COPY_IGNORE_SCHEMATAS:
        for field in _get_schemata_fields(obj, schemata):
            yield field.getName()

def _get_all_field(obj):
    return obj.Schema().keys()

def _copy_fields(obj):
    all_field_set = set(_get_all_field(obj))
    ignore_field_set = set(_get_ignore_fields_in_schematas(obj)) | \
                            COPY_IGNORE_FIELDS
    copy_fields = all_field_set - ignore_field_set
    for field_name in copy_fields:
        dic = {'field_name' : field_name}
        field = obj.getField(field_name)
        if ITextField in providedBy(field):
            dic['contenttype'] = field.getContentType(obj)
            dic['data'] = field.getRaw(obj)
        elif IFileField in providedBy(field):
            field_data = field.getRaw(obj)
            if field_data:
                dic['filename'] = field.getFilename(obj)
                dic['data'] = field_data.data
        elif IBlobField in providedBy(field):
            field_data = field.getRaw(obj)
            if field_data:
                dic['filename'] = field_data.getFilename()
                dic['data'] = field_data.data
                dic['is_blob'] = True
        else:
            dic['data'] = field.getRaw(obj)
        yield dic

def _generate_unique_id(type_name=None):
    now = DateTime()
    time = '%s.%s' % (now.strftime('%Y-%m-%d'), str(now.millis())[7:])
    rand = str(random())[2:6]
    prefix = ''
    suffix = ''
    if type_name is not None:
        prefix = type_name.replace(' ', '_')+'.'
    prefix = prefix.lower()
    return prefix + time + rand + suffix

class ContentPaste(BrowserView):
    
    def __call__(self):
        msg = ""
        try:
            new_obj = self.create_new_obj()
        except ConflictError:
            raise
        except (Unauthorized, 'Unauthorized'):
            msg = _(u'Unauthorized to paste item(s).')
        except: # fallback
            msg = _(u'New content could not create for duplicate.')
        if msg:
            self.context.plone_utils.addPortalMessage(msg, 'error')
            raise


        msg = _(u"Duplicate new content")
        self.context.plone_utils.addPortalMessage(msg, 'info')
        self.context.REQUEST.RESPONSE.redirect(new_obj.absolute_url() + '/edit')
        return None
    
    def create_new_obj(self):
        container = aq_parent(self.context)
        obj = self.context
        new_id = _generate_unique_id(obj.portal_type)
        new_obj_id = container.invokeFactory(obj.portal_type, new_id)
        new_obj = getattr(container, new_obj_id)
        for field_dic in _copy_fields(obj):
            field_name = field_dic['field_name']
            data  = field_dic.get('data', '')
            filename = field_dic.get('filename', None)
            contenttype = field_dic.get('contenttype', None)
            if field_name == 'title':
                adding_data = translate(ADDING_TITLE, context=self.request)
                if isinstance(data, unicode):
                    data_save = adding_data + data
                else:
                    data_save = adding_data.encode('utf-8') + data
            else:
                data_save = data
            field = new_obj.getField(field_name)
            if data_save:
                field.set(new_obj, data_save)
            if filename is not None:
                if field_dic.get('is_blob', False):
                    field.getRaw(new_obj).setFilename(filename)
                else:
                    field.setFilename(new_obj, filename)
            if contenttype is not None:
                field.setContentType(new_obj, contenttype)
        new_obj._renameAfterCreation(check_auto_id=True)
        new_obj.reindexObject()

        return new_obj
