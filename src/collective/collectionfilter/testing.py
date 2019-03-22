# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.collectionfilter


class CollectiveCollectionFilterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.collectionfilter)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.collectionfilter:default')


COLLECTIVE_COLLECTIONFILTER_FIXTURE = CollectiveCollectionFilterLayer()


COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_COLLECTIONFILTER_FIXTURE,),
    name='CollectiveCollectionFilterLayer:IntegrationTesting',
)


COLLECTIVE_COLLECTIONFILTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_COLLECTIONFILTER_FIXTURE,),
    name='CollectiveCollectionFilterLayer:FunctionalTesting',
)


COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_COLLECTIONFILTER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveCollectionFilterLayer:AcceptanceTesting',
)
