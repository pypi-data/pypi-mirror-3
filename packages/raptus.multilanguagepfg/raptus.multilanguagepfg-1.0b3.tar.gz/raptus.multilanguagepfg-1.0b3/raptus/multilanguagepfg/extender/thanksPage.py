from zope.component import adapts

from archetypes.schemaextender.interfaces import ISchemaExtender

from raptus.multilanguagefields import widgets
from raptus.multilanguageplone.extender import fields
from raptus.multilanguageplone.extender.base import DefaultExtender

from Products.ATContentTypes.configuration import zconf

from Products.PloneFormGen.content.thanksPage import FormThanksPage
from Products.PloneFormGen import PloneFormGenMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage

class ThanksPageExtender(DefaultExtender):

    adapts(FormThanksPage)

    FROM_BASE_SCHEMA = ('title','description',)
    
    fields = [
              
        fields.TextField('thanksPrologue',
            schemata='default',
            required=False,
            searchable=False,
            primary=False,
            storage=AnnotationStorage(migrate=True),
            validators = ('isTidyHtmlWithCleanup',),
            default_content_type = zconf.ATDocument.default_content_type,
            default_output_type = 'text/x-html-safe',
            allowable_content_types = zconf.ATDocument.allowed_content_types,
            widget = widgets.RichWidget(
                label = _(u"label_thanksprologue_text", default=u"Thanks Prologue"),
                description = _(u"help_thanksprologue_text", default=u"This text will be displayed above the selected field inputs."),
                rows = 8,
                allow_file_upload = zconf.ATDocument.allow_document_upload,
                ),
            ),
        fields.TextField('thanksEpilogue',
            schemata='default',
            required=False,
            searchable=False,
            primary=False,
            storage=AnnotationStorage(migrate=True),
            validators = ('isTidyHtmlWithCleanup',),
            default_content_type = zconf.ATDocument.default_content_type,
            default_output_type = 'text/x-html-safe',
            allowable_content_types = zconf.ATDocument.allowed_content_types,
            widget = widgets.RichWidget(
                label = _(u"label_thanksepilogue_text", default=u"Thanks Epilogue"),
                description = _(u"help_thanksepilogue_text", default=u"The text will be displayed after the field inputs."),
                rows = 8,
                allow_file_upload = zconf.ATDocument.allow_document_upload,
                ),
            ),
        fields.TextField('noSubmitMessage',
            schemata='default',
            required=False,
            searchable=False,
            primary=False,
            storage=AnnotationStorage(migrate=True),
            validators = ('isTidyHtmlWithCleanup',),
            default_content_type = zconf.ATDocument.default_content_type,
            default_output_type = 'text/x-html-safe',
            default="""
                <p>No input was received. Please <a title="Test Folder" href=".">visit the form</a>.</p>
                """,
            allowable_content_types = zconf.ATDocument.allowed_content_types,
            widget = widgets.RichWidget(
                label = _(u"label_nosubmit_text", default=u"No Submit Message"),
                description = _(u"help_nosubmit_text", default=u"""
                    The text to display if the browser reaches this
                    thanks page without submitting a form. Typically, this
                    would direct the reader to the form.
                    """),
                rows = 4,
                allow_file_upload = zconf.ATDocument.allow_document_upload,
                ),
            ),
        ]

    fields = fields + [f for f in DefaultExtender.fields if f.getName() in FROM_BASE_SCHEMA]




   