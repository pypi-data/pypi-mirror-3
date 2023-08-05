from zope.interface import implements, Interface

from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.registry.interfaces import IRegistry

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from collective.flattr import flattrMessageFactory as _
from collective.flattr.interfaces import ICollectiveFlattr
import urllib2
import base64
from urllib import urlencode
import simplejson

from Products.statusmessages.interfaces import IStatusMessage


class IFlattr(Interface):
    """
    oauth view interface
    """


class Flattr(BrowserView):
    """
    oauth browser view
    """
    implements(IFlattr)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def registry(self):
        return getUtility(IRegistry).forInterface(ICollectiveFlattr)

    @property
    def customer_key(self):
        return self.registry.customer_key

    @property
    def customer_secret(self):
        return self.registry.customer_secret

    @property
    def consumer(self):
        key = self.customer_key
        secret = self.customer_secret
        if key and secret:
            return {'key': key, 'secret': secret}
        return None

    @property
    def authorize_url(self):
        return self.registry.authorize_url

    @property
    def access_token_url(self):
        return self.registry.access_token_url

    @property
    def access_token(self):
        token = self.registry.access_token
        token_type = self.registry.access_token_type
        if token and token_type:
            return {'Authorization': '%s %s' %(token_type, token)}
        return None

    @property
    def opener(self):
        opener = urllib2.build_opener()
        token = self.registry.access_token
        token_type = self.registry.access_token_type
        if token and token_type:
            opener.addheaders = [('Authorization',
                '%s %s' % (token_type, token))]
        else:
            key = self.registry.customer_key
            secret = self.registry.customer_secret
            b64up = base64.encodestring('%s:%s' % (key, secret))\
                .replace('\n','')
            opener.addheaders = [('Authorization',
                'Basic %s' % b64up)]

        return opener

    def __call__(self):
        """  """
        code = self.request.get('code', None)
        error = self.request.get('error', None)
        error_description = self.request.get('error_description', u'')

        if code and not isinstance(code, unicode):
            code = safe_unicode(code)
        if error and not isinstance(error, unicode):
            error = safe_unicode(error)
        if error_description and not isinstance(error_description, unicode):
            error_description = safe_unicode(error_description)

        status = IStatusMessage(self.request)

        if code and not error:
            ret = self.getAccessToken(code)
            if u'access_token' in ret and u'token_type' in ret\
                and u'error' not in ret:

                self._setAccessToken(ret['access_token'],
                    ret['token_type'])

                status.addStatusMessage(
                    _(u'collective.flattr successfully configured'),
                    type='info')
            else:
                if u'error' in ret and u'error_description' in ret:
                    error = ret['error']
                    error_description = ret['error_description']
                else:
                    error = _(u'undefined')
                    error_description = _(u'Undefined error while getting access token')

        if error:
            status.addStatusMessage('%s: %s' % (error, error_description),
                type='error')

        self.request.response.redirect(self.portal.absolute_url())
        return

    def getAccessToken(self, code):
        """ Returns the access token """
        key = self.customer_key
        secret = self.customer_secret
        token = self.access_token

        if token:
            return {'error': _(u'token_configured'),
                'error_description': _(u'access token already configured')}

        if not key or not secret:
            return {'error': _(u'no_customer'),
                'error_description': _(u'no customer_key or customer_secret configured')}

        headers = {'Content-Type': 'application/json'}

        params = {'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': '%s/collective_flattr' % (self.context.absolute_url())}

        req = urllib2.Request(self.access_token_url,
            data=simplejson.dumps(params),
            headers=headers)

        ret = {}
        try:
            retf = self.opener.open(req)
            if retf:
                ret = retf.read()
        except urllib2.HTTPError, e:
            ret = e.read()
        return simplejson.loads(ret)

    def _setAccessToken(self, token, token_type):
        """ Sets values in registry """
        if not isinstance(token, unicode):
            token = safe_unicode(token)
        if not isinstance(token_type, unicode):
            token_type = safe_unicode(token_type)
        self.registry.access_token = token
        self.registry.access_token_type = token_type.capitalize()

    def getThings(self, count=30, page=1, next=False):
        """ Returns a list of flattr things """
        param = [('count', count),
            ('page', page)]
        params = urlencode(param)
        url = 'https://api.flattr.com/rest/v2/user/things'
        ret = {'next_page': False, 'data': []}
        ret['data'] = self._json_call(url, params,
            error_ret=[])

        # Ask flattr for the next count things, if there are some, we have a
        # next page.
        if not next and ret['data']:
            sec_ret = self.getThings(count=count, page=page+1, next=True)
            if sec_ret['data']:
                ret['next_page'] = True

        return ret

    def _json_call(self, url, data=None, error_ret=[]):
        """ Returns the result of a json call to url """
        req = urllib2.Request(url, data=data)
        try:
            retf = self.opener.open(req)
            if retf:
                return simplejson.loads(retf.read())
        except urllib2.HTTPError:
            pass
        return error_ret

    def getLanguages(self):
        """ Returns flattr languages """
        return self._json_call('https://api.flattr.com/rest/v2/languages')

    def getCategories(self):
        """ Returns flattr categories """
        return self._json_call('https://api.flattr.com/rest/v2/categories')

    def _getParams(self, title, url=None, description=None, category=None,
        language=None, tags=None, hidden=False, patch=None):
        """ Returns param string """
        param = [
            ('title', title),
            ('hidden', hidden),
        ]
        if url:
            param.append(('url', url))
        if description:
            param.append(('description', description))
        if category:
            param.append(('category', category))
        if language:
            param.append(('language', language))
        if tags:
            param.append(('tags', tags))
        if patch:
            param.append(('_method', patch))
        return urlencode(param)

    def createThing(self, title, url, description=None, category=None,
        language=None, tags=None, hidden=False, patch=None):
        """ Create a thing on flattr and return the result """
        params = self._getParams(title,
                                 url=url,
                                 description=description,
                                 category=category,
                                 language=language,
                                 tags=tags,
                                 hidden=hidden,
                                 patch=patch)
        return self._json_call('https://api.flattr.com/rest/v2/things',
            data=params, error_ret={})

    def updateThing(self, title, thingid, description=None, category=None,
        language=None, tags=None, hidden=False, patch='patch'):
        """ Update a thing on flattr and return the result """
        params = self._getParams(title,
                                 description=description,
                                 category=category,
                                 language=language,
                                 tags=tags,
                                 hidden=hidden,
                                 patch=patch)
        return self._json_call(
            'https://api.flattr.com/rest/v2/things/%s' % thingid,
            data=params, error_ret={})


class FlattrPopup(BrowserView):

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def __init__(self, context, request):
        super(FlattrPopup, self).__init__(context, request)

        self.flattr = getMultiAdapter((self.portal, self.request),
            name='collective_flattr')

    def getThings(self):
        page = self.request.get('page', 1)
        return self.flattr.getThings(page=page)

    def getPrevUrl(self):
        prev_page = self.request.get('page', 1) - 1
        field_name = self.request.get('fieldName', '')
        if prev_page <= 0:
            return None
        return '%s/%s?page:int=%s&fieldName=%s' % (self.context.absolute_url(),
            'flattr_popup', prev_page, field_name)

    def getNextUrl(self):
        next_page = self.request.get('page', 1) + 1
        field_name = self.request.get('fieldName', '')
        return '%s/%s?page:int=%s&fieldName=%s' % (self.context.absolute_url(),
            'flattr_popup', next_page, field_name)
