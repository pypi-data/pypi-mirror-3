import unittest2 as unittest
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from collective.flattr.tests.base import COLLECTIVE_FLATTR_INTEGRATION_TESTING

class as_manager(object):
    def __init__(self, portal):
        self.portal = portal

    def __enter__(self):
        setRoles(self.portal, TEST_USER_ID, ('Manager',))
        return self.portal.restrictedTraverse('@@flattr_helper')

    def __exit__(self, type, value, traceback):
        setRoles(self.portal, TEST_USER_ID, ('Member',))

class TestFlattrHelper(unittest.TestCase):

    layer = COLLECTIVE_FLATTR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Member',))

    def test_getFlattrUrl(self):
        with as_manager(self.portal) as view:
            ret = view.getFlattrUrl()
            self.assertEquals(ret, u'http://api.flattr.com')

            # try the same thing with https:// in requests url
            self.layer['request']['URL'] = u'https://nohost/plone'

            ret = view.getFlattrUrl()
            self.assertEquals(ret, u'https://api.flattr.com')
