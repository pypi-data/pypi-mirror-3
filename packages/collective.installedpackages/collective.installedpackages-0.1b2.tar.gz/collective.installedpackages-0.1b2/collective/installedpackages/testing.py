#coding=utf8
from .config import PACKAGE_NAME
from plone.app.testing import IntegrationTesting, PLONE_FIXTURE, PloneSandboxLayer

class PackageLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.installedpackages
        self.loadZCML(package=collective.installedpackages)        

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, '%s:default' % PACKAGE_NAME)

FIXTURE = PackageLayer()
INTEGRATION_TESTING = IntegrationTesting(bases=(FIXTURE,), name='%s:Integration' % PACKAGE_NAME)
