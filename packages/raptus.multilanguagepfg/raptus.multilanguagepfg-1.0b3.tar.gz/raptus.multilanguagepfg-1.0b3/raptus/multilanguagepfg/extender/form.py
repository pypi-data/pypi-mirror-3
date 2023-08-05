from zope.component import adapts

from archetypes.schemaextender.interfaces import ISchemaExtender

from raptus.multilanguagefields import widgets
from raptus.multilanguageplone.extender import fields
from raptus.multilanguageplone.extender.folder import FolderExtender

from Products.ATContentTypes.configuration import zconf
from Products.Archetypes.atapi import AnnotationStorage

from Products.PloneFormGen.content.form import FormFolder
from Products.PloneFormGen import PloneFormGenMessageFactory as _


class FormFolderExtender(FolderExtender):

    adapts(FormFolder)
    
    fields = FolderExtender.fields + [
        fields.StringField('submitLabel',
            storage=AnnotationStorage(migrate=True),
            required=0,
            searchable=0,
            default=_("Submit"),
            widget=widgets.StringWidget(
                label=_(u'label_submitlabel_text', default=u"Submit Button Label"),
                description = _(u'help_submitlabel_text', default=u""),
            ),
        ),
        fields.StringField('resetLabel',
            storage=AnnotationStorage(migrate=True),
            required=0,
            searchable=0,
            default=_("Reset"),
            widget=widgets.StringWidget(
                    label=_(u'label_reset_button', default=u"Reset Button Label"),
            ),
        ),
        fields.TextField('formPrologue',
            storage=AnnotationStorage(migrate=True),
            schemata='default',
            required=False,
            # Disable search to bypass a unicode decode error
            # in portal_catalog indexes.
            searchable=False,
            primary=False,
            validators = ('isTidyHtmlWithCleanup', ),
            default_content_type = zconf.ATDocument.default_content_type,
            default_output_type = 'text/x-html-safe',
            allowable_content_types = zconf.ATDocument.allowed_content_types,
            widget = widgets.RichWidget(
                label = _(u'label_prologue_text', default=u"Form Prologue"),
                description = _(u'help_prologue_text',
                    default=u"This text will be displayed above the form fields."),
                rows = 8,
                allow_file_upload = zconf.ATDocument.allow_document_upload,
            ),
        ),
        fields.TextField('formEpilogue',
            storage=AnnotationStorage(migrate=True),
            schemata='default',
            required=False,
            # Disable search to bypass a unicode decode error
            # in portal_catalog indexes.
            searchable=False,
            primary=False,
            validators = ('isTidyHtmlWithCleanup', ),
            default_content_type = zconf.ATDocument.default_content_type,
            default_output_type = 'text/x-html-safe',
            allowable_content_types = zconf.ATDocument.allowed_content_types,
            widget = widgets.RichWidget(
                label = _(u'label_epilogue_text', default=u"Form Epilogue"),
                description = _(u'help_epilogue_text',
                    default=u"The text will be displayed after the form fields."),
                rows = 8,
                allow_file_upload = zconf.ATDocument.allow_document_upload,
            ),
        ),
    ]
    




    
