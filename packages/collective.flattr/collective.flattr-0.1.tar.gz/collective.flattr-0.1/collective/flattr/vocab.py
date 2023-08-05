from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.flattr import flattrMessageFactory as _
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

buttons_vocab = SimpleVocabulary(
    [SimpleTerm(value=u'Large Counter', title=_(u'Large Counter')),
     SimpleTerm(value=u'Compact Counter', title=_(u'Compact Counter')),
     SimpleTerm(value=u'Static', title=_(u'Static')),
     ]
    )

def flattrCategoryVocab(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    flattr = getMultiAdapter((portal, context.REQUEST),
        name='collective_flattr')
    categories = flattr.getCategories()
    terms = []
    for cat in categories:
        terms.append(SimpleVocabulary.createTerm(cat['id'],
                                                 cat['id'],
                                                 cat['text']))
    return SimpleVocabulary(terms)

def flattrLanguageVocab(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    flattr = getMultiAdapter((portal, context.REQUEST),
        name='collective_flattr')
    languages = flattr.getLanguages()
    terms = [SimpleVocabulary.createTerm('sysdefault',
        'sysdefault', _(u'System default'))]
    for lang in languages:
        terms.append(SimpleVocabulary.createTerm(lang['id'],
                                                 lang['id'],
                                                 lang['text']))
    return SimpleVocabulary(terms)
