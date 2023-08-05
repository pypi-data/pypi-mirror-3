import unittest2 as unittest
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import z2

from collective.flattr.tests.base import COLLECTIVE_FLATTR_INTEGRATION_TESTING
from collective.flattr.browser.viewlets import FlattrViewlet
from collective.flattr.interfaces import ICollectiveFlattr


class TestFlattrViewlet(unittest.TestCase):

    layer = COLLECTIVE_FLATTR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager',))
        self.portal.invokeFactory('Document', 'tester')
        self.folder = self.portal.tester
        self.folder.flattrThingId = u'XXX'
        self.viewlet = FlattrViewlet(self.folder, self.layer['request'], None)
        setRoles(self.portal, TEST_USER_ID, ('Member',))

    def test_update_default(self):
        self.viewlet.update()

        self.assertEquals(self.viewlet.button_type, u'flattr;button:compact;')
        self.assertTrue(self.viewlet.show)

    def test_update_compact(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.button_type = u'Compact Counter'

        self.viewlet.update()
        self.assertEquals(self.viewlet.button_type, u'flattr;button:compact;')
        self.assertTrue(self.viewlet.show)

    def test_update_large(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.button_type = u'Large Counter'

        self.viewlet.update()
        self.assertEquals(self.viewlet.button_type, u'flattr;button:large;')
        self.assertTrue(self.viewlet.show)

    def test_update_static(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.button_type = u'Static'

        self.viewlet.update()
        self.assertEquals(self.viewlet.button_type, u'')
        self.assertTrue(self.viewlet.show)

    def test_no_thing_url(self):
        self.folder.flattrThingId = u''

        self.viewlet.update()
        self.assertFalse(self.viewlet.show)

    def test_base_url(self):
        self.viewlet.update()

        self.assertEquals(self.viewlet.base_url, u'http://nohost/plone/tester')

    def test_ct_no_fthing_url(self):
        delattr(self.folder, 'flattrThingId')

        self.viewlet.update()
        self.assertFalse(self.viewlet.show)

    def test_update_when_not_installed(self):
        app = self.portal.aq_parent
        z2.uninstallProduct(app, 'collective.flattr')
        from Products.CMFCore.utils import getToolByName
        setup = getToolByName(self.portal, 'portal_setup')
        setup.runAllImportStepsFromProfile(
            'profile-collective.flattr:uninstall')

        self.viewlet.update()
        self.assertFalse(self.viewlet.show)

    def test_http_img_url_static(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.button_type = u'Static'

        self.viewlet.update()
        self.assertEquals(self.viewlet.flattr_url, u'http://api.flattr.com')

        ret = self.viewlet.render()

        self.failUnless(u'src="http://api.flattr.com/button' in ret)

    def test_https_img_url_static(self):
        # and again with https in requests url
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.button_type = u'Static'
        self.layer['request']['URL'] = u'https://nohost/plone'

        self.viewlet.update()
        self.assertEquals(self.viewlet.flattr_url, u'https://api.flattr.com')

        ret = self.viewlet.render()

        self.failUnless(u'src="https://api.flattr.com/button' in ret)

    def test_http_img_url_not_static(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.button_type = u'Large Counter'

        self.viewlet.update()
        self.assertEquals(self.viewlet.flattr_url, u'http://api.flattr.com')

        ret = self.viewlet.render()

        self.failUnless(u'src="http://api.flattr.com/button' in ret)

    def test_https_img_url_not_static(self):
        # and again with https in requests url
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.button_type = u'Compact Counter'
        self.layer['request']['URL'] = u'https://nohost/plone'

        self.viewlet.update()
        self.assertEquals(self.viewlet.flattr_url, u'https://api.flattr.com')

        ret = self.viewlet.render()

        self.failUnless(u'src="https://api.flattr.com/button' in ret)
