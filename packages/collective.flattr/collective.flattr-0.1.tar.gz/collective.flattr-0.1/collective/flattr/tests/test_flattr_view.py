import unittest2 as unittest
import urllib2
from AccessControl import Unauthorized
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.flattr.interfaces import ICollectiveFlattr
from mocker import Mocker
from Products.statusmessages.interfaces import IStatusMessage
from collective.flattr.tests.mocks import MockOpener

from collective.flattr.tests.base import COLLECTIVE_FLATTR_INTEGRATION_TESTING

class as_manager(object):
    def __init__(self, portal):
        self.portal = portal

    def __enter__(self):
        setRoles(self.portal, TEST_USER_ID, ('Manager',))
        return self.portal.restrictedTraverse('@@collective_flattr')

    def __exit__(self, type, value, traceback):
        setRoles(self.portal, TEST_USER_ID, ('Member',))


class TestFlattrView(unittest.TestCase):
    
    layer = COLLECTIVE_FLATTR_INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Member',))

    def test_permissions(self):
        # only cmf.ManagePortal has access!
        error = False
        try:
            self.portal.restrictedTraverse('@@collective_flattr')
        except Unauthorized:
            error = True
        self.assertTrue(error)

    def test_access_token_url(self):
        with as_manager(self.portal) as view:
            ret = view.access_token_url
            self.assertEquals(ret,
                u'https://flattr.com/oauth/token')

    def test_authorize_url(self):
        with as_manager(self.portal) as view:
            ret = view.authorize_url
            self.assertEquals(ret,
                u'https://flattr.com/oauth/authorize')

    def test_registry(self):
        with as_manager(self.portal) as view:
            ret = view.registry
            self.assertEquals(ret.__dict__,
                getUtility(IRegistry).forInterface(ICollectiveFlattr).\
                    __dict__)

    def test_access_token_empty(self):
        with as_manager(self.portal) as view:
            ret = view.access_token
            self.failUnless(ret is None)

    def test_access_token(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.access_token = u'8843d7f92416211de9ebb963ff4ce28125932878'
        reg.access_token_type = u'Bearer'

        with as_manager(self.portal) as view:
            ret = view.access_token
            self.assertTrue(isinstance(ret, dict))
            
            self.assertEquals(ret['Authorization'],
                u'Bearer 8843d7f92416211de9ebb963ff4ce28125932878')

    def test_consumer_empty(self):
        with as_manager(self.portal) as view:
            ret = view.consumer
            self.failUnless(ret is None)

    def test_consumer(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.customer_key = u'mycustomer'
        reg.customer_secret = u'mysecret'

        with as_manager(self.portal) as view:
            ret = view.consumer
            self.assertTrue(isinstance(ret, dict))

            self.assertEquals(ret['key'], u'mycustomer')
            self.assertEquals(ret['secret'], u'mysecret')

    def test_setAccessToken(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        with as_manager(self.portal) as view:
            view._setAccessToken(u'a', u'bearer')

            self.assertEquals(reg.access_token, u'a')
            self.assertEquals(reg.access_token_type, u'Bearer')

            view._setAccessToken(u'c', u'bearer')

            self.assertEquals(reg.access_token, u'c')
            self.assertEquals(reg.access_token_type, u'Bearer')

    def test_setAccessToken_no_unicode(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        with as_manager(self.portal) as view:
            view._setAccessToken('a', 'bearer')

            self.assertEquals(reg.access_token, u'a')
            self.assertEquals(reg.access_token_type, u'Bearer')

            view._setAccessToken('c', 'bearer')

            self.assertEquals(reg.access_token, u'c')
            self.assertEquals(reg.access_token_type, u'Bearer')

    def test_getAccessToken_no_customer(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        with as_manager(self.portal) as view:
            reg.customer_key = u'customer'
            ret = view.getAccessToken(1234)

            self.assertEquals(ret['error'], u'no_customer')
            self.assertEquals(ret['error_description'],
                u'no customer_key or customer_secret configured')

            reg.customer_key = u''
            reg.customer_secret = u'secret'

            self.assertEquals(ret['error'], u'no_customer')
            self.assertEquals(ret['error_description'],
                u'no customer_key or customer_secret configured')

            reg.customer_key = u''
            reg.customer_secret = u''

            self.assertEquals(ret['error'], u'no_customer')
            self.assertEquals(ret['error_description'],
                u'no customer_key or customer_secret configured')

    def test_getAccessToken_token_configured(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.customer_key = u'customer'
        reg.customer_secret = u'secret'

        with as_manager(self.portal) as view:
            reg.access_token = u'token'
            reg.access_token_type = u'Bearer'
            ret = view.getAccessToken(1234)

            self.assertEquals(ret['error'], u'token_configured')
            self.assertEquals(ret['error_description'],
                u'access token already configured')

    def test_getAccessToken(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.customer_key = u'customer'
        reg.customer_secret = u'secret'

        with as_manager(self.portal) as view:
            mocker = Mocker()

            obj = mocker.patch(view)
            obj.opener
            mocker.result(MockOpener('{"access_token":"NEW_ACCESS_TOKEN","token_type":"bearer"}',
                verify_data=lambda x: x.get_full_url()==u'https://flattr.com/oauth/token' and x.data=='{"redirect_uri": "http://nohost/plone/collective_flattr", "code": 1234, "grant_type": "authorization_code"}' and x.headers=={'Content-type': 'application/json'}))

            obj.opener
            mocker.result(MockOpener('{"error":"invalid_request","error_description":"error desc"}',
                error=True,
                verify_data=lambda x: x.get_full_url()==u'https://flattr.com/oauth/token' and x.data=='{"redirect_uri": "http://nohost/plone/collective_flattr", "code": 1234, "grant_type": "authorization_code"}' and x.headers=={'Content-type': 'application/json'}
                ))

            with mocker:
                ret = view.getAccessToken(1234)
                self.failUnless(u'error' not in ret)
                self.failUnless(u'error_description' not in ret)
                self.failUnless(u'access_token' in ret)
                self.failUnless(u'token_type' in ret)

                self.assertEquals(ret['access_token'], u'NEW_ACCESS_TOKEN')
                self.assertEquals(ret['token_type'], u'bearer')

                # second call get an inner status of != 200 and
                # will return None
                ret = view.getAccessToken(1234)
                self.failUnless(u'error' in ret)
                self.failUnless(u'error_description' in ret)
                self.failUnless(u'access_token' not in ret)
                self.failUnless(u'token_type' not in ret)

                self.assertEquals(ret['error'], u'invalid_request')
                self.assertEquals(ret['error_description'], u'error desc')

    def test_opener(self):
        from collective.flattr.browser.flattr import Flattr

        view = Flattr(self.portal, self.layer['request'])

        ret = view.opener
        self.assertTrue(isinstance(ret, urllib2.OpenerDirector))

    def test_opener_authorization(self):
        from collective.flattr.browser.flattr import Flattr
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.access_token = u'TOKEN'
        reg.access_token_type = u'Bearer'

        view = Flattr(self.portal, self.layer['request'])

        ret = view.opener
        self.assertTrue(isinstance(ret, urllib2.OpenerDirector))

        self.assertEquals(ret.addheaders, [('Authorization', 'Bearer TOKEN')])

    def test_opener_base_auth(self):
        from collective.flattr.browser.flattr import Flattr
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.access_token = u''
        reg.access_token_type = u''
        reg.customer_key = u'USER'
        reg.customer_secret = u'PASS'

        view = Flattr(self.portal, self.layer['request'])

        ret = view.opener
        self.assertTrue(isinstance(ret, urllib2.OpenerDirector))

        self.assertEquals(ret.addheaders, [('Authorization', 'Basic VVNFUjpQQVNT')])

    def test_getLanguages(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('[{"id": "de_DE", "text": "German"}, {"id": "en_US", "text": "English"}]'))

        with mocker:
            ret = view.getLanguages()

            self.failUnless(isinstance(ret, list))
            self.assertEquals(len(ret), 2)
            self.assertEquals(ret[0], {'id': u'de_DE',
                'text': u'German'})
            self.assertEquals(ret[1], {'id': u'en_US',
                'text': u'English'})

    def test_getLanguages_HTTPError(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('[{"id": "de_DE", "text": "German"}, {"id": "en_US", "text": "English"}]', error=True))

        with mocker:
            ret = view.getLanguages()

            self.failUnless(isinstance(ret, list))
            self.assertEquals(len(ret), 0)

    def test_getCategories(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('[{"id": "text", "text": "Text"}, {"id": "images", "text": "Images"}]'))

        with mocker:
            ret = view.getCategories()

            self.failUnless(isinstance(ret, list))
            self.assertEquals(len(ret), 2)
            self.assertEquals(ret[0], {'id': u'text',
                'text': u'Text'})
            self.assertEquals(ret[1], {'id': u'images',
                'text': u'Images'})

    def test_getCategories_HTTPError(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('[{"id": "text", "text": "Text"}, {"id": "images", "text": "Images"}]', error=True))

        with mocker:
            ret = view.getCategories()

            self.failUnless(isinstance(ret, list))
            self.assertEquals(len(ret), 0)

    def test_getParams(self):
        from collective.flattr.browser.flattr import Flattr

        view = Flattr(self.portal, self.layer['request'])

        ret = view._getParams(u'Hello')
        self.assertEquals(ret, 'title=Hello&hidden=False')

        ret = view._getParams(u'Hello',
            url=u'http://localhost/',
            description='desc',
            category='cat',
            language='de_DE',
            tags='a,b',
            patch='patch',
            hidden=True)

        self.assertEquals(ret, 'title=Hello&hidden=True&url=http%3A%2F%2Flocalhost%2F&description=desc&category=cat&language=de_DE&tags=a%2Cb&_method=patch')

    def test_createThing(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('{ "id": 431547, "link": "https://api.flattr.dev/rest/v2/things/431547", "message": "ok", "description": "Thing was created successfully" }', verify_data = lambda x: x.get_data() == 'title=Hello&hidden=True&url=http%3A%2F%2Flocalhost%2F&description=desc&category=cat&language=de_DE&tags=a%2Cb'))

        with mocker:
            ret = view.createThing(u'Hello',
                url=u'http://localhost/',
                description='desc',
                category='cat',
                language='de_DE',
                tags='a,b',
                hidden=True)

            self.assertEquals(ret, {'id': 431547,
                'link': u'https://api.flattr.dev/rest/v2/things/431547',
                'message': u'ok',
                'description': u'Thing was created successfully' })

    def test_createThing_wrong_data(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('{ "id": 431547, "link": "https://api.flattr.dev/rest/v2/things/431547", "message": "ok", "description": "Thing was created successfully" }', verify_data = lambda x: x.get_data() == 'title=Hello&hidden=True&url=http%3A%2F%2Flocalhost%2F&description=desc&category=cat&language=de_DE&tags=a%2Cb'))

        with mocker:
            ret = False
            try:
                view.createThing(u'Hello',
                    url=u'http://localhost/',
                    description='desc',
                    category='cat',
                    language='en_DE',
                    tags='a,b',
                    hidden=True)
            except ValueError:
                ret = True
            self.assertTrue(ret)

    def test_createThing_HTTPError(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('{ "id": 431547, "link": "https://api.flattr.dev/rest/v2/things/431547", "message": "ok", "description": "Thing was created successfully" }', verify_data = lambda x: x.get_data() == 'title=Hello&hidden=True&url=http%3A%2F%2Flocalhost%2F&description=desc&category=cat&language=de_DE&tags=a%2Cb', error=True))

        with mocker:
            ret = view.createThing(u'Hello',
                url=u'http://localhost/',
                description='desc',
                category='cat',
                language='de_DE',
                tags='a,b',
                hidden=True)

            self.assertEquals(ret, {})

    def test_updateThing(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('{ "message": "ok", "description": "Thing was updated successfully" }', verify_data = lambda x: x.get_full_url().endswith('431547') and x.get_data() == 'title=Hello&hidden=True&description=desc&category=cat&language=de_DE&tags=a%2Cb&_method=patch'))

        with mocker:
            ret = view.updateThing(u'Hello',
                431547,
                description='desc',
                category='cat',
                language='de_DE',
                tags='a,b',
                hidden=True)

            self.assertEquals(ret, {'message': u'ok',
                'description': u'Thing was updated successfully' })

    def test_updateThing_HTTPError(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('{ "message": "ok", "description": "Thing was updated successfully" }', verify_data = lambda x: x.get_full_url().endswith('431547') and x.get_data() == 'title=Hello&hidden=True&description=desc&category=cat&language=de_DE&tags=a%2Cb&_method=patch', error=True))

        with mocker:
            ret = view.updateThing(u'Hello',
                431547,
                description='desc',
                category='cat',
                language='de_DE',
                tags='a,b',
                hidden=True)

            self.assertEquals(ret, {})

    def test_getThing(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        def test_func(x):
            return 'count=30&page=' in x.get_data()
        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('[ { "type": "thing", "resource": "https://api.flattr.dev/rest/v2/things/1", "link": "https://flattr.dev/thing/1", "id": 1 }, { "type": "thing", "resource": "https://api.flattr.dev/rest/v2/things/2", "link": "https://flattr.dev/thing/2", "id": 2} ]', verify_data=test_func))
        obj.opener
        mocker.result(MockOpener('', verify_data=test_func, error=True))

        with mocker:
            ret = view.getThings()
            self.failUnless(u'data' in ret)
            self.failUnless(u'next_page' in ret)

            self.assertFalse(ret['next_page'])

            self.assertEquals(ret['data'][0], { "type": "thing", "resource": "https://api.flattr.dev/rest/v2/things/1", "link": "https://flattr.dev/thing/1", "id": 1 })
            self.assertEquals(ret['data'][1], { "type": "thing", "resource": "https://api.flattr.dev/rest/v2/things/2", "link": "https://flattr.dev/thing/2", "id": 2})

    def test_getThing_with_next(self):
        from collective.flattr.browser.flattr import Flattr

        mocker = Mocker()
        view = Flattr(self.portal, self.layer['request'])

        obj = mocker.patch(view)
        obj.opener
        mocker.result(MockOpener('[ { "type": "thing", "resource": "https://api.flattr.dev/rest/v2/things/1", "link": "https://flattr.dev/thing/1", "id": 1 }, { "type": "thing", "resource": "https://api.flattr.dev/rest/v2/things/2", "link": "https://flattr.dev/thing/2", "id": 2} ]', verify_data=lambda x: 'count=30&page=' in x.get_data()))
        mocker.count(2)
        # if the same thing is called twice, it is called for the first page
        # and again for the second page. So there is a result, what means that
        # there is a next page

        with mocker:
            ret = view.getThings()
            self.failUnless(u'data' in ret)
            self.failUnless(u'next_page' in ret)

            self.assertTrue(ret['next_page'])

            self.assertEquals(ret['data'][0], { "type": "thing", "resource": "https://api.flattr.dev/rest/v2/things/1", "link": "https://flattr.dev/thing/1", "id": 1 })
            self.assertEquals(ret['data'][1], { "type": "thing", "resource": "https://api.flattr.dev/rest/v2/things/2", "link": "https://flattr.dev/thing/2", "id": 2})

class TestFlattrViewCall(unittest.TestCase):
    
    layer = COLLECTIVE_FLATTR_INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Member',))

    def test_call_access_denied(self):
        with as_manager(self.portal) as view:
            from collective.flattr.browser.flattr import Flattr
            view = Flattr(self.portal, self.layer['request'])
            ret = view()

            self.layer['request']['error'] = u'access_denied'
            self.layer['request']['error_description'] = u'error description'
            ret = view()
            self.assertEquals(self.layer['request'].response\
                .headers['location'], 'http://nohost/plone')
            ret = IStatusMessage(self.layer['request'])\
                .showStatusMessages()[0]
            self.assertEquals(ret.message, u'access_denied: error description')
            self.assertEquals(ret.type, u'error')

    def test_call_invalid_request(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.access_token = u''

        mocker = Mocker()
        func = mocker.replace('collective.flattr.browser.flattr.Flattr.getAccessToken')
        func(u'un8Vzv7pNMXNuAQY3uRgjYfM4V3Feirz')
        mocker.result({'error': u'invalid_request',
            'error_description': u'error desc'})

        with as_manager(self.portal) as view:
            ## need the real class here, not the wrapped one, to get mocker
            ## working
            from collective.flattr.browser.flattr import Flattr

            with mocker:
                view = Flattr(self.portal, self.layer['request'])
                self.layer['request']['code'] = u'un8Vzv7pNMXNuAQY3uRgjYfM4V3Feirz'
                ret = view()
                self.assertEquals(self.layer['request'].response\
                    .headers['location'], 'http://nohost/plone')
                ret = IStatusMessage(self.layer['request'])\
                    .showStatusMessages()[0]
                self.assertEquals(ret.message, u'invalid_request: error desc')
                self.assertEquals(ret.type, u'error')

    def test_call_valid(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.access_token = u''

        mocker = Mocker()
        func = mocker.replace('collective.flattr.browser.flattr.Flattr.getAccessToken')
        func(u'un8Vzv7pNMXNuAQY3uRgjYfM4V3Feirz')
        mocker.result({'access_token': u'NEW_ACCESS_TOKEN',
            'token_type': u'bearer'})

        with as_manager(self.portal) as view:
            ## need the real class here, not the wrapped one, to get mocker
            ## working
            from collective.flattr.browser.flattr import Flattr

            with mocker:
                self.layer['request']['code'] = u'un8Vzv7pNMXNuAQY3uRgjYfM4V3Feirz'
                view = Flattr(self.portal, self.layer['request'])

                ret = view()
                self.assertEquals(reg.access_token, u'NEW_ACCESS_TOKEN')
                self.assertEquals(self.layer['request'].response\
                    .headers['location'], 'http://nohost/plone')
                ret = IStatusMessage(self.layer['request'])\
                    .showStatusMessages()[0]
                self.assertEquals(ret.message,
                    u'collective.flattr successfully configured')
                self.assertEquals(ret.type, u'info')

    def test_call_no_unicode_and_error(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.access_token = u''

        with as_manager(self.portal) as view:
            from collective.flattr.browser.flattr import Flattr
            self.layer['request']['code'] = 'un8Vzv7pNMXNuAQY3uRgjYfM4V3Feirz'
            self.layer['request']['error'] = 'test'
            self.layer['request']['error_description'] = 'test error'
            view = Flattr(self.portal, self.layer['request'])

            ret = view()
            self.assertEquals(reg.access_token, u'')
            self.assertEquals(self.layer['request'].response\
                .headers['location'], 'http://nohost/plone')
            ret = IStatusMessage(self.layer['request'])\
                .showStatusMessages()
            self.assertEquals(ret[0].message,
                u'test: test error')
            self.assertEquals(ret[0].type, u'error')

    def test_call_no_unicode_and_no_error_desc(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.access_token = u''

        mocker = Mocker()
        func = mocker.replace('collective.flattr.browser.flattr.Flattr.getAccessToken')
        func(u'un8Vzv7pNMXNuAQY3uRgjYfM4V3Feirz')
        mocker.result({'access_token': u'NEW_ACCESS_TOKEN',
            'token_type': u'bearer', 'error': u'blubber'})

        with as_manager(self.portal) as view:
            from collective.flattr.browser.flattr import Flattr
            with mocker:
                self.layer['request']['code'] = 'un8Vzv7pNMXNuAQY3uRgjYfM4V3Feirz'
                view = Flattr(self.portal, self.layer['request'])

                ret = view()
                self.assertEquals(reg.access_token, u'')
                self.assertEquals(self.layer['request'].response\
                    .headers['location'], 'http://nohost/plone')
                ret = IStatusMessage(self.layer['request'])\
                    .showStatusMessages()
                self.assertEquals(ret[0].message,
                    u'undefined: Undefined error while getting access token')
                self.assertEquals(ret[0].type, u'error')
