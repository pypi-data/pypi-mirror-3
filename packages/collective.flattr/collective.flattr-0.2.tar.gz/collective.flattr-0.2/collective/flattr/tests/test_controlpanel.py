import unittest2 as unittest
from mocker import Mocker
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from plone.registry.interfaces import IRegistry
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.interfaces import IFormLayer

from collective.flattr.tests.base import COLLECTIVE_FLATTR_INTEGRATION_TESTING
from collective.flattr.interfaces import ICollectiveFlattr
from collective.flattr.browser.flattr import Flattr
from collective.flattr.tests.mocks import MockOpener

# have to split into test_controlpanel.py and test_controlpanel_call.py,
# because mocker does not like duplicate replaces. 


class controlpanel(object):
    def __init__(self, portal, request):
        self.portal = portal
        self.request = request

    def __enter__(self):
        return getMultiAdapter((self.portal, self.request),
            name='flattr-controlpanel')

    def __exit__(self, type, value, traceback):
        pass


class TestControlPanel(unittest.TestCase):

    layer = COLLECTIVE_FLATTR_INTEGRATION_TESTING



    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager',))

        self.reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        self.mocker = None
        alsoProvides(self.layer['request'], IFormLayer)

    def tearDown(self):
        if self.mocker:
            self.mocker.reset()

    def test_test_access_token_fail(self):
        self.reg.access_token = u'NEW'
        self.reg.access_token_type = u'Bearer'
        self.mocker = Mocker()

        flattr_view = self.mocker.patch(Flattr)

        flattr_view.opener
        self.mocker.result(MockOpener('{"error": "unauthorized", "error_description": "Hello World"}', error=True, verify_data=lambda x: x.get_full_url()==u'https://api.flattr.com/rest/v2/user' and x.headers=={'Content-type':'application/json'}))


        self.layer['request'].form = {'form.button.TestAccessToken': True}
        with self.mocker:
            with controlpanel(self.portal, self.layer['request']) as view:
                ret = view._handleTestAccessToken()

                self.assertFalse(ret)

                self.assertEquals(view.test_access_token,
                    u'Configured access token does not work :(')
                ret = IStatusMessage(self.layer['request'])\
                    .showStatusMessages()[0]
                self.assertEquals(ret.type, u'error')
                self.assertEquals(ret.message,
                    u'Configured access token does not work :(')

    def test_test_access_token_success(self):
        self.reg.access_token = u'NEW'
        self.reg.access_token_type = u'Bearer'
        self.mocker = Mocker()

        flattr_view = self.mocker.patch(Flattr)
        flattr_view.opener
        self.mocker.result(MockOpener('{"username": "Hello World"}', verify_data=lambda x: x.get_full_url()==u'https://api.flattr.com/rest/v2/user' and x.headers=={'Content-type':'application/json'}))

        self.layer['request'].form = {'form.button.TestAccessToken': True}
        with self.mocker:
            with controlpanel(self.portal, self.layer['request']) as view:
                # call again... then it works
                ret = view._handleTestAccessToken()

                self.failUnless(u'username' in view.test_access_token)
                self.failUnless(u'Hello World' in view.test_access_token)

                # call again. without access token
                self.reg.access_token = u''
                self.reg.access_token_type = u''
                ret = view._handleTestAccessToken()

                self.assertFalse(ret)
                ret = IStatusMessage(self.layer['request'])\
                    .showStatusMessages()[0]
                self.assertEquals(ret.type, u'error')
                self.assertEquals(ret.message, u'No access token configured')

    def test_authenticate(self):

        self.layer['request'].form = {'form.button.Save': True}
        with controlpanel(self.portal, self.layer['request']) as view:
            self.reg.customer_key = u''
            ret = view._handleAuthenticate()

            self.assertFalse(ret)

            ret = IStatusMessage(self.layer['request'])\
                .showStatusMessages()[0]
            self.assertEquals(ret.type, u'error')
            self.assertEquals(ret.message, u'Unable to create authorize '
                'url. consumer and consumer_secret not configured :(')

            # call again for success
            self.reg.customer_key = u'consumer'
            ret = view._handleAuthenticate()
            redirect = self.layer['request'].response.headers['location']
            
            self.assertTrue(ret)
            self.failUnless(redirect.startswith(self.reg.authorize_url))
            self.failUnless(u'collective_flattr' in redirect)
            self.failUnless(u'client_id=consumer' in redirect)
            self.failUnless(u'redirect_uri' in redirect)
            self.failUnless(u'scope=thing' in redirect)
            self.failUnless(u'response_type=code' in redirect)

    def test_clear_access_token(self):
        self.layer['request'].form = {'form.button.ClearAccessToken': True}
        self.reg.access_token = u'my access token'
        self.reg.access_token_type = u'my access token secret'
        with controlpanel(self.portal, self.layer['request']) as view:
            ret = view._handleClearAccessToken()

            self.assertTrue(ret)

            msg = IStatusMessage(self.layer['request']).showStatusMessages()[0]
            self.assertEquals(msg.type, u'info')
            self.assertEquals(msg.message, u'Cleared access token')

            self.assertEquals(self.reg.access_token, u'')
            self.assertEquals(self.reg.access_token_type, u'')
