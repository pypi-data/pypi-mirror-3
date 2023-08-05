from zope.component import adapts

from archetypes.schemaextender.interfaces import ISchemaExtender

from raptus.multilanguagefields import widgets
from raptus.multilanguageplone.extender import fields
from raptus.multilanguageplone.extender.base import DefaultExtender

from raptus.multilanguagepfg.extender import BaseFormFieldExtender

from Products.PloneFormGen.content.fieldset import FieldsetFolder
from Products.PloneFormGen import PloneFormGenMessageFactory as _


class FieldsetFolderExtender(BaseFormFieldExtender):
    
    adapts(FieldsetFolder)
    
    fields = DefaultExtender.fields + [] #make a new list
    description = [f for f in fields if f.getName() == 'description'][0]
    fields.remove(description)
    description = description.copy()
    description.widget.label = _(u'label_fieldsethelp_text', default=u'Fieldset Help')
    description.widget.description = None
    fields.append(description)
    
    def getFields(self):
        return self.fields