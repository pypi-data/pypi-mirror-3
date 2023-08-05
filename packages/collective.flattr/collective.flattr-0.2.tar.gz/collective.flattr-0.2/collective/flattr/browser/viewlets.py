from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.flattr.interfaces import ICollectiveFlattr


class FlattrViewlet(ViewletBase):
    render = ViewPageTemplateFile('flattr.pt')

    def update(self):
        super(FlattrViewlet, self).update()

        self.show = False
        registry = getUtility(IRegistry)
        try:
            proxy = registry.forInterface(ICollectiveFlattr)
        except KeyError:
            # This occurs if collective.flattr is not installed.
            return

        try:
            thing_id = self.context.flattrThingId
            self.thing_url = u'https://flattr.com/thing/%s' % thing_id
            if thing_id:
                self.show = True
        except AttributeError:
            pass
        if not self.show:
            return
        
        button_type = u'flattr;button:large;'
        if proxy.button_type == u'Compact Counter':
            button_type = u'flattr;button:compact;'
        elif proxy.button_type == u'Static':
            button_type = u''

        self.button_type = button_type
        self.base_url = self.context.absolute_url()
        self.flattr_url = self.context.restrictedTraverse('@@flattr_helper')\
            .getFlattrUrl()
