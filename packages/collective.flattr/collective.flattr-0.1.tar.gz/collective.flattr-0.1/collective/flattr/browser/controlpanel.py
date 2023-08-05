from zope.component import getMultiAdapter
from collective.flattr import flattrMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as __
from collective.flattr.interfaces import ICollectiveFlattr
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.registry.browser import controlpanel
from z3c.form import button
from pprint import pformat
import simplejson as json
import urllib2


class ControlPanel(controlpanel.RegistryEditForm):

    schema = ICollectiveFlattr
    label = _(u'collective.flattr Settings')
    description = _(u'Change settings of collective.flattr')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.flattr = getMultiAdapter((self.context, self.request), name='collective_flattr')
        self.test_access_token = None
        self.view_name = self.request.get('URL', '').split('/')[-1]

    def updateFields(self):
        super(ControlPanel, self).updateFields()
        fields = self.fields.omit('base_url')
        fields = fields.omit('access_token')
        fields = fields.omit('access_token_type')
        fields = fields.omit('access_token_url')
        fields = fields.omit('authorize_url')
        self.fields = fields

    def __call__(self):

        if 'form.button.TestAccessToken' in self.request.form:
            self._handleTestAccessToken()
        elif 'form.button.AcquireToken' in self.request.form:
            ret = self._handleAuthenticate()
            if ret:
                return
        elif 'form.button.ClearAccessToken' in self.request.form:
            self._handleClearAccessToken()
        elif 'form.button.Cancel' in self.request.form:
            IStatusMessage(self.request).add(__(u'Edit cancelled.'), type='info')

        return super(ControlPanel, self).__call__()

    def updateWidgets(self):
        super(ControlPanel, self).updateWidgets()

    def showObtainAccessToken(self):
        return self.flattr.customer_key.strip()\
            and self.flattr.customer_secret.strip()

    render = ViewPageTemplateFile('controlpanel.pt')

    @button.buttonAndHandler(__(u"Save"), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).add(_(u"Changes saved."), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.view_name))

    @button.buttonAndHandler(__(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).add(_(u"Edit cancelled."), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.view_name))


    def _handleAuthenticate(self):
        """ Handle click on form.button.Save """
        client_id = self.flattr.customer_key
        if client_id:
            callback_uri = '%s/collective_flattr' %\
                self.context.absolute_url()

            self.request.response.redirect('%s?scope=thing&response_type=code'
                '&redirect_uri=%s&client_id=%s' % (
                    self.flattr.authorize_url,
                    callback_uri,
                    client_id))
            return True
        IStatusMessage(self.request).add(_( u'Unable to create authorize '
            'url. consumer and consumer_secret not configured :('),
            type='error')
        return False

    def _handleTestAccessToken(self):
        """ Handle click on form.button.TestAccessToken """
        headers = {'Content-Type': 'application/json'}
        access_token = self.flattr.access_token
        if not access_token:
            IStatusMessage(self.request).add(
                _(u'No access token configured'), type='error')
            self.test_access_token = u''
            return False
        req = urllib2.Request('https://api.flattr.com/rest/v2/user', headers=headers)

        ret = False
        try:
            retf = self.flattr.opener.open(req)
            if retf:
                self.test_access_token = pformat(json.loads(retf.read()))
                return True
        except urllib2.HTTPError, e:
            IStatusMessage(self.request).add(
                _(u'Configured access token does not work :('), type='error')
            self.test_access_token = _(u'Configured access token does not work :(')
        return False

    def _handleClearAccessToken(self):
        """ Handle click on form.button.ClearAccessToken """
        self.flattr._setAccessToken(u'', u'')
        IStatusMessage(self.request).add(
            _(u'Cleared access token'), type='info')
        return True
