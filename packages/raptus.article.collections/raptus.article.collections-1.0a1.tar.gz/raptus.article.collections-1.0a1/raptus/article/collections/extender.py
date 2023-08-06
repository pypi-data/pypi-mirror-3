from zope.interface import implements
from zope.component import adapts

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from plone.indexer.interfaces import IIndexer

from Products.Archetypes import atapi
from Products.ZCatalog.interfaces import IZCatalog

try: # Plone 4 and higher
    from Products.ATContentTypes.interfaces.topic import IATTopic
except: # BBB Plone 3
    from Products.ATContentTypes.interface.topic import IATTopic

from raptus.article.core.componentselection import ComponentSelectionWidget
from raptus.article.core import RaptusArticleMessageFactory as _

class LinesField(ExtensionField, atapi.LinesField):
    """ LinesField
    """

class StringField(ExtensionField, atapi.StringField):
    """ StringField
    """

class CollectionExtender(object):
    """ Adds the component selection field to the topic content type
    """
    implements(ISchemaExtender)
    adapts(IATTopic)

    fields = [
        StringField('more',
            required = False,
            searchable = False,
            storage = atapi.AnnotationStorage(),
            schemata = 'settings',
            widget = atapi.StringWidget(
                description = _(u'description_more', default=u'Custom text used for read more links in article components displaying this collection.'),
                label= _(u'label_more', default=u'More link'),
            )
        ),
        LinesField('components',
            enforceVocabulary = True,
            vocabulary_factory = 'componentselectionvocabulary',
            storage = atapi.AnnotationStorage(),
            schemata = 'settings',
            widget = ComponentSelectionWidget(
                description = _(u'description_component_selection_collection', default=u'Select the components in which this collection should be displayed.'),
                label= _(u'label_component_selection', default=u'Component selection'),
            )
        ),
    ]

    def __init__(self, context):
         self.context = context
         
    def getFields(self):
        return self.fields

class Index(object):
    implements(IIndexer)
    adapts(IATTopic, IZCatalog)
    def __init__(self, obj, catalog):
        self.obj = obj
    def __call__(self):
        return self.obj.Schema()['components'].get(self.obj)
