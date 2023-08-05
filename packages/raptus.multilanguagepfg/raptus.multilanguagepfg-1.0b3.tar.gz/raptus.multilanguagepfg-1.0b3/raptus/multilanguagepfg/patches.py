from raptus.multilanguagepfg import LOG
from raptus.multilanguagepfg import config
from raptus.multilanguagepfg.extender import BaseFormFieldExtender, FieldsetFolderExtender

from zope.component import queryAdapter

from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.PloneFormGen.content.form import FormFolder

from Products.PloneFormGen.content.fieldsBase import StringVocabularyField, LinesVocabularyField
from Products.PloneFormGen.content.likertField import LikertField
from Products.CMFCore.Expression import getExprContext
from Products.Archetypes.utils import shasattr


_getFieldObjects_old = FormFolder._getFieldObjects
def _getFieldObjects(self, objTypes=None, includeFSMarkers=False):
    """ return list of enclosed fields """

    # This function currently checks to see if
    # an object is a form field by looking to see
    # if it has an fgField attribute.

    # Make sure we look through fieldsets
    if objTypes is not None:
        objTypes = list(objTypes)[:]
        objTypes.append('FieldsetFolder')

    myObjs = []

    for obj in self.objectValues(objTypes):
        # use shasattr to make sure we're not aquiring
        # fgField by acquisition

        # TODO: If I stick with this scheme for enable overrides,
        # I'm probably going to want to find a way to cache the result
        # in the request. _getFieldObjects potentially gets called
        # several times in a request.

        # first, see if the field enable override is set
        if shasattr(obj, 'fgTEnabled') and obj.getRawFgTEnabled():
            # process the override enabled TALES expression
            # create a context for expression evaluation
            context = getExprContext(self, obj)
            # call the tales expression, passing our custom context
            enabled = obj.getFgTEnabled(expression_context=context)
        else:
            enabled = True

        if enabled:
            if shasattr(obj, 'fgField'):
                myObjs.append(obj)
            if shasattr(obj, 'fieldsetFields'):
                if queryAdapter(obj, interface=ISchemaExtender, name=config.PROJECT_NAME + FieldsetFolderExtender.__name__):
                    # Product is not installed --> nothing to patch
                    obj.setTitle(obj.Title())
                    obj.setDescription(obj.Description())
                myObjs += obj.fieldsetFields(objTypes, includeFSMarkers)

    for field in myObjs:

        if not queryAdapter(field, interface=ISchemaExtender, name=config.PROJECT_NAME + BaseFormFieldExtender.__name__):
            # Product is not installed --> nothing to patch
            continue
        
        field.setTitle(field.Title())
        field.setDescription(field.Description())
        if hasattr(field,'setFgDefault'):
            field.setFgDefault(field.getFgDefault())
        if isinstance(field.fgField, (StringVocabularyField, LinesVocabularyField,)):
            field.fgVocabulary = field.getFgVocabulary()
        if isinstance(field.fgField, LikertField):
            field.setLikertAnswers(field.getLikertAnswers())
            field.setLikertQuestions(field.getLikertQuestions())
    
    return myObjs

FormFolder._getFieldObjects = _getFieldObjects
LOG.info("Products.PloneFormGen.content.form.FormFolder._getFieldObjects patched")