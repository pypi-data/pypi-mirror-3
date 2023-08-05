from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import z2
from Products.CMFCore.utils import getToolByName


class ContentGovernanceLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.contentgovernance

        self.loadZCML(package=collective.contentgovernance)
        z2.installProduct(app, 'collective.contentgovernance')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'collective.contentgovernance')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.contentgovernance:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'test-folder')
        setRoles(portal, TEST_USER_ID, ['Member'])
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser('foobar', 'secret', ['Member'], [])

CG_FIXTURE = ContentGovernanceLayer()
CG_INTEGRATION_TESTING = IntegrationTesting(bases=(CG_FIXTURE, ),
    name="ContentGovernanceLayer:Integration")
CG_FUNCTIONAL_TESTING = FunctionalTesting(bases=(CG_FIXTURE, ),
    name="ContentGovernanceLayer:Functional")
