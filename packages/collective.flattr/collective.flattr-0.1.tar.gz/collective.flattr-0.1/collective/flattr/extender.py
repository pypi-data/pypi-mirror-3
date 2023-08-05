from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import BooleanField
from Products.ATContentTypes.interface import IATContentType
from collective.flattr import flattrMessageFactory as _
from collective.flattr.widget import FlattrThingWidget


class MyStringField(ExtensionField, StringField):
    """ A trivial field """


class MyBooleanField(ExtensionField, BooleanField):
    """ A trivial bool field """


class FlattrExtender(object):
    adapts(IATContentType)
    implements(ISchemaExtender)

    fields = [
        MyStringField('flattrThingId',
            schemata=_(u'Flattr'),
            widget=FlattrThingWidget(
                label=_(u'Id of your thing'),
                description=_(u'Id of your thing, e.g. 408580 for http://flattr.com/thing/408580/Chris-wirre-Gedankenwelt'),
            )
        ),
        MyBooleanField('flattrCreateThing',
            schemata=_(u'Flattr'),
            default=False,
            widget=BooleanWidget(
                label=_(u'Create thing'),
                description=_(u'Create a thing on flattr automatically after create and update.'),
            )
        ),
        MyBooleanField('flattrHidden',
            schemata=_(u'Flattr'),
            default=False,
            widget=BooleanWidget(
                label=_(u'Hide thing'),
                description=_(u'Thing is not shown in Flattr listings.'),
            )
        ),
        MyStringField('flattrCategory',
            schemata=_(u'Flattr'),
            vocabulary_factory='collective.flattr.categories',
            widget=SelectionWidget(
                label=_(u'Category'),
                description=_(u'Category of your content'),
            ),
        ),
        MyStringField('flattrLanguage',
            schemata=_(u'Flattr'),
            vocabulary_factory='collective.flattr.languages',
            widget=SelectionWidget(
                label=_(u'Language'),
                description=_('Language of your content'),
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
