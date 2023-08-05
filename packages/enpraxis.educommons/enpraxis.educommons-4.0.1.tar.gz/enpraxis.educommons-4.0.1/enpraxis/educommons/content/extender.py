from Products.Archetypes.public import StringField
from Products.Archetypes.atapi import MultiSelectionWidget
from archetypes.schemaextender.field import ExtensionField
from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from Products.Archetypes.public import BooleanWidget
from Products.ATContentTypes.interface import IATDocument
from enpraxis.educommons import eduCommonsMessageFactory as _
from enpraxis.educommons.interfaces import IeduCommonsBrowserLayer


oer_type_vocab = [
    _(u'Syllabus'),
    _(u'Schedule'),
    _(u'Lecture Notes'),
    _(u'Assignment'),
    _(u'Project'),
    _(u'Readings'),
    _(u'Image Gallery'),
    _(u'Video'),
    _(u'Audio'),
    _(u'Interactive'),
    _(u'Textbook'),
    ]
        
         
class OERTypeField(ExtensionField, StringField):
    """ A string field added to basic archetypes. """


class OERTypeExtender(object):
    """ An extension to default archetypes schemas for basic objects. """

    adapts(IATDocument)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IeduCommonsBrowserLayer

    fields = [
        OERTypeField('oerType',
                     required=False,
                     isMetadata=True,
                     vocabulary=oer_type_vocab,
                     default=None,
                     widget=MultiSelectionWidget(
                         label=_(u'OER Type'),
                         label_msgid='label_oer_type',
                         description=_(u'The type of resourse'),
                         description_msgid=_(u'help_oer_type'),
                         format='select',
                         ),
                     ),
        ]

    def __init__(self, context):
        self.context = context
        
    def getFields(self):
        return self.fields

                                            
