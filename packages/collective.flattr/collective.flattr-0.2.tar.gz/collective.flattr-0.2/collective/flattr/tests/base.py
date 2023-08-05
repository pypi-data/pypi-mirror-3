from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2


class CollectiveFlattr(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.flattr
        self.loadZCML(package=collective.flattr)

        z2.installProduct(app, 'collective.flattr')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.flattr:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'collective.flattr')

COLLECTIVE_FLATTR_FIXTURE = CollectiveFlattr()
COLLECTIVE_FLATTR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_FLATTR_FIXTURE,),
    name="CollectiveFlattr:Integration")
COLLECTIVE_FLATTR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_FLATTR_FIXTURE,),
    name="CollectiveFlattr:Functional")
