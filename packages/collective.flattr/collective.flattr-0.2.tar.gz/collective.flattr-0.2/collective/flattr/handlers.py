from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.utils import safe_hasattr
from collective.flattr import flattrMessageFactory as _

def create_flattr_thing(event):
    obj = event.object
    portal = getToolByName(obj, 'portal_url').getPortalObject()
    flattr = getMultiAdapter((portal, obj.REQUEST), name='collective_flattr')

    if safe_hasattr(obj, 'flattrCreateThing')\
        and safe_hasattr(obj, 'flattrThingId'):

        if obj.flattrCreateThing and not obj.flattrThingId:
            category = None
            language = None
            tags = None
            hidden = 'false'
            if safe_hasattr(obj, 'flattrCategory') and obj.flattrCategory:
                category = obj.flattrCategory
            if safe_hasattr(obj, 'flattrLanguage') and obj.flattrLanguage != 'sysdefault':
                language = obj.flattrLanguage
            if safe_hasattr(obj, 'flattrHidden') and obj.flattrHidden:
                hidden = 'true'
            if not language:
                default_lang = obj.restrictedTraverse('@@plone_portal_state')\
                    .default_language()
                language = '%s_%s' % (default_lang, default_lang.upper())
            if obj.Subject():
                tags = ','.join(obj.Subject())
            ret = flattr.createThing(obj.Title(),
                obj.absolute_url(),
                description=obj.Description(),
                category=category,
                language=language,
                tags=tags)
            if 'message' in ret and ret['message'] == u'ok' and 'id' in ret:
                obj.flattrThingId = ret['id']
                obj.reindexObject()
                IStatusMessage(obj.REQUEST).addStatusMessage(
                    _(u'Created Flattr thing'),
                    type='info')
            else:
                IStatusMessage(obj.REQUEST).addStatusMessage(
                    _(u'Was not able to create a thing on Flattr'),
                    type='error')

def update_flattr_thing(event):
    obj = event.object
    portal = getToolByName(obj, 'portal_url').getPortalObject()
    flattr = getMultiAdapter((portal, obj.REQUEST), name='collective_flattr')
    if safe_hasattr(obj, 'flattrCreateThing')\
        and obj.flattrCreateThing\
        and safe_hasattr(obj, 'flattrThingId'):

        if obj.flattrCreateThing and not obj.flattrThingId:
            create_flattr_thing(event)
            return

        category = None
        language = None
        tags = None
        hidden = 'false'
        if safe_hasattr(obj, 'flattrCategory') and obj.flattrCategory:
            category = obj.flattrCategory
        if safe_hasattr(obj, 'flattrLanguage') and obj.flattrLanguage != 'sysdefault':
            language = obj.flattrLanguage
        if safe_hasattr(obj, 'flattrHidden') and obj.flattrHidden:
            hidden = 'true'
        if not language:
            default_lang = obj.restrictedTraverse('@@plone_portal_state')\
                .default_language()
            language = '%s_%s' % (default_lang, default_lang.upper())
        if obj.Subject():
            tags = ','.join(obj.Subject())
        thingid = obj.flattrThingId.split('/')[-1]
        ret = flattr.updateThing(obj.Title(),
            thingid,
            description=obj.Description(),
            category=category,
            language=language,
            tags=tags,
            hidden=hidden)
        if 'message' in ret and ret['message'] == u'ok':
            obj.reindexObject()
            IStatusMessage(obj.REQUEST).addStatusMessage(
                _(u'Updated Flattr thing'),
                type='info')
        else:
            IStatusMessage(obj.REQUEST).addStatusMessage(
                _(u'Was not able to update the thing on Flattr'),
                type='error')
