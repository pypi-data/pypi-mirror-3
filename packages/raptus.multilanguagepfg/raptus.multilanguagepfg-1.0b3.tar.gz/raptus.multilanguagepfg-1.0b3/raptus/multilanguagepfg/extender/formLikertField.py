from zope.component import adapts

from archetypes.schemaextender.interfaces import ISchemaExtender

from raptus.multilanguagefields import widgets
from raptus.multilanguageplone.extender import fields
from raptus.multilanguageplone.extender.base import DefaultExtender

from Products.ATContentTypes.configuration import zconf
from Products.Archetypes.Field import TextField, LinesField, StringField
from Products.Archetypes.atapi import AnnotationStorage

from Products.PloneFormGen.content.formLikertField import FGLikertField, default_questions, default_answers
from Products.PloneFormGen import PloneFormGenMessageFactory as _


class FGLikertFieldExtender(DefaultExtender):

    adapts(FGLikertField)

    fields = [
        fields.LinesField('likertQuestions',
            searchable=0,
            required=1,
            default=default_questions,
            storage=AnnotationStorage(migrate=True),
            widget=widgets.LinesWidget(
                label=_(u'label_fglikert_questions', default=u'Questions'),
                description = _(u'help_fglikert_questions',
                    default=u"""List of questions; these will be the rows of the table."""),
            ),
        ),

        fields.LinesField('likertAnswers',
            searchable=0,
            required=1,
            default=default_answers,
            storage=AnnotationStorage(migrate=True),
            widget=widgets.LinesWidget(
                label=_(u'label_fglikert_answers', default=u'Answers'),
                description = _(u'help_fglikert_answers',
                default=u"""List of possible answers for each of the questions;
                    these will be the columns of the table."""),
            ),
        ),
    ]

