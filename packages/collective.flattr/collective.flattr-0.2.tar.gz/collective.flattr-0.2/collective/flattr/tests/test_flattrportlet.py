# -*- coding: utf-8 -*-
import unittest2 as unittest
import logging
from zope.component import getUtility, getMultiAdapter
from plone.registry.interfaces import IRegistry

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from collective.flattr.interfaces import ICollectiveFlattr

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from collective.flattr.portlets import flattrportlet
from collective.flattr.tests.base import COLLECTIVE_FLATTR_INTEGRATION_TESTING
from collective.flattr.tests.mocks import MockLoggingHandler


logger = logging.getLogger('collective.flattr')


class TestPortlet(unittest.TestCase):

    layer = COLLECTIVE_FLATTR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal
        setRoles(self.portal, TEST_USER_ID, ('Manager',))

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='collective.flattr.portlets.FlattrPortlet')
        self.assertEquals(portlet.addview, 'collective.flattr.portlets.FlattrPortlet')

    def test_interfaces(self):
        portlet = flattrportlet.Assignment(button_type=u'Static',
            thing_url=u'http://example.com/thing1',
            text=u'Hello World')
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

        self.assertEquals(portlet.button_type, u'Static')
        self.assertEquals(portlet.thing_url, u'http://example.com/thing1')
        self.assertEquals(portlet.text, u'Hello World')

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name='collective.flattr.portlets.FlattrPortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={u'button_type': u'Static',
            u'thing_url': u'http://example.com/thing1',
            u'text': u'Hello World'})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], flattrportlet.Assignment))
        portlet = mapping.values()[0]
        self.assertEquals(portlet.button_type, u'Static')
        self.assertEquals(portlet.thing_url, u'http://example.com/thing1')
        self.assertEquals(portlet.text, u'Hello World')

    # NOTE: This test can be removed if the portlet has no edit form
    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = flattrportlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, flattrportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = flattrportlet.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, flattrportlet.Renderer))
        self.assertEquals(assignment.button_type, u'Large Counter')
        self.assertEquals(assignment.thing_url, u'')
        self.assertEquals(assignment.text, u'')


class TestRenderer(unittest.TestCase):

    layer = COLLECTIVE_FLATTR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal
        setRoles(self.portal, TEST_USER_ID, ('Manager',))
        self.handler = MockLoggingHandler()
        logger.addHandler(self.handler)

    def tearDown(self):
        self.handler.reset()
        logger.removeHandler(self.handler)

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or flattrportlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render_static(self):
        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment(
            button_type=u'Static',
            thing_url=u'thing/1',
            text=u'Hello World'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless(u'Hello World' in output)
        self.failUnless(u'http://flattr.com/thing/thing/1' in output)

    def test_render(self):
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.base_url = u'http://myexample.com'
        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment(
            button_type=u'Compact Counter',
            thing_url=u'thing/1',
            text=u'Hello World'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless(u'Hello World' in output)
        self.failUnless(u'http://myexample.com' in output)
        self.failUnless(u'http://flattr.com/thing/thing/1' in output)

    def test_transformed(self):
        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment())
        r = r.__of__(self.folder)
        r.update()
        r.data.text = 'Hällö'

        ret = r.transformed()
        self.assertEquals(ret, u'Hällö')
        self.failUnless('Flattr portlet at http://nohost/plone has stored '
            'non-unicode text. Assuming utf-8 encoding' in 
            '\n'.join(self.handler.messages['warning']))

    def test_transformed_empty(self):
        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment())
        r = r.__of__(self.folder)
        r.update()
        r.data.text = u''

        ret = r.transformed()
        self.assertEquals(ret, None)

    def test_transformed_string(self):
        # test if the text also can be None
        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment())
        r = r.__of__(self.folder)
        r.update()
        r.data.text = None

        ret = r.transformed()
        self.assertEquals(ret, None)

    def test_update_not_installed(self):
        app = self.portal.aq_parent
        reg = getUtility(IRegistry).forInterface(ICollectiveFlattr)
        reg.base_url = u'http://example.com'
        from plone.testing import z2
        z2.uninstallProduct(app, 'collective.flattr')
        from Products.CMFCore.utils import getToolByName
        setup = getToolByName(self.portal, 'portal_setup')
        setup.runAllImportStepsFromProfile(
            'profile-collective.flattr:uninstall')

        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment())
        r = r.__of__(self.folder)

        r.update()
        self.assertEquals(r.base_url, u'http://nohost')

    def test_http_img_url_static(self):
        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment(
            button_type=u'Static',
            thing_url=u'thing/1',
            text=u'Hello World'))
        r = r.__of__(self.folder)

        r.update()
        self.assertEquals(r.flattr_url, u'http://api.flattr.com')

        ret = r.render()

        self.failUnless(u'src="http://api.flattr.com/button' in ret)

    def test_https_img_url_static(self):
        # and again with https in requests url
        self.layer['request']['URL'] = u'https://nohost/plone'

        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment(
            button_type=u'Static',
            thing_url=u'thing/1',
            text=u'Hello World'))
        r = r.__of__(self.folder)

        r.update()
        self.assertEquals(r.flattr_url, u'https://api.flattr.com')

        ret = r.render()

        self.failUnless(u'src="https://api.flattr.com/button' in ret)

    def test_http_img_url_not_static(self):
        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment(
            button_type=u'Large Counter',
            thing_url=u'thing/1',
            text=u'Hello World'))
        r = r.__of__(self.folder)

        r.update()
        self.assertEquals(r.flattr_url, u'http://api.flattr.com')

        ret = r.render()

        self.failUnless(u'src="http://api.flattr.com/button' in ret)

    def test_https_img_url_not_static(self):
        # and again with https in requests url
        self.layer['request']['URL'] = u'https://nohost/plone'
        r = self.renderer(context=self.portal, assignment=flattrportlet.Assignment(
            button_type=u'Compact Counter',
            thing_url=u'thing/1',
            text=u'Hello World'))
        r = r.__of__(self.folder)

        r.update()
        self.assertEquals(r.flattr_url, u'https://api.flattr.com')

        ret = r.render()

        self.failUnless(u'src="https://api.flattr.com/button' in ret)
