from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.ATContentTypes.interface import IATContentType
from Products.Archetypes.atapi import StringField, SelectionWidget
from Products.Archetypes.interfaces import IFieldDefaultProvider
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import implements, directlyProvides
from zope.site.hooks import getSite
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.contentgovernance import messageFactory as _


class ExtendedStringField(ExtensionField, StringField):
    """The responsible user field
    """

    def get(self, instance, **kwargs):
        value = StringField.get(self, instance, **kwargs)
        if value is None:
            return ''
        return value

    def set(self, instance, value, **kwargs):
        if value is not None:
            creators = list(instance.Creators())
            if value in creators:
                creators.remove(value)
            creators.insert(0, value)
            instance.setCreators(creators)
        StringField.set(self, instance, value, **kwargs)
        pu = getToolByName(instance, 'plone_utils')
        try:
            pu.changeOwnershipOf(instance, value)
        except KeyError:
            pass


class ContentTypeExtender(object):
    """Adapter that adds the responsible person field.
    """

    adapts(IATContentType)
    implements(ISchemaExtender)

    _fields = [
        ExtendedStringField("responsibleperson",
            languageIndependent = False,
            schemata='ownership',
            vocabulary_factory='collective.contentgovernance.AvailableUsersVocabulary',
            widget = SelectionWidget(
                label = _(u"label_responsibleperson_title",
                default=u"Responsible person"),
                description = _(u"help_responsibleperson",
                default=u"The person responsible for updating this content."),
            ),
            write_permission='collective.contentgovernance: Change responsible person'
        )]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields


def AvailableUsersVocabularyFactory(context):
    """Vocabulary factory for supplying a vocabulary of users in the site for
       the injected responsible person field
    """
    directlyProvides(IVocabularyFactory)
    pas_view = getMultiAdapter((context, context.REQUEST), name='pas_search')
    items = [SimpleTerm(r['userid'],
                        r['userid'],
                        'description' in r and r['description'] or r['userid'])
             for r in pas_view.searchUsers()]
    items.insert(0, SimpleTerm('', '', 'Nobody'))
    return SimpleVocabulary(items)


def DefaultResponsiblePersonFactory(context):
    """A factory to provide the default to the responsible person field.
    """
    return DefaultResponsiblePerson()


class DefaultResponsiblePerson(object):
    """adapter for supplying default value for the responsible person field
    """

    adapts(IATContentType)
    implements(IFieldDefaultProvider)

    def __call__(self):
        pm = getToolByName(getSite(), 'portal_membership')
        return pm.getAuthenticatedMember().getUserName()
