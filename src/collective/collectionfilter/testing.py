# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.textfield.value import RichTextValue
from plone.testing import z2


class CollectiveCollectionFilterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.mosaic
        self.loadZCML(package=plone.app.mosaic)
        import collective.geolocationbehavior
        self.loadZCML(package=collective.geolocationbehavior)
        import collective.collectionfilter
        self.loadZCML(package=collective.collectionfilter)
        self.loadZCML(package=collective.collectionfilter.tests)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.mosaic:default')
        applyProfile(portal, 'collective.geolocationbehavior:default')
        applyProfile(portal, 'collective.collectionfilter:default')
        applyProfile(portal, 'collective.collectionfilter.tests:testing')

        with api.env.adopt_roles(['Manager']):
            portal.invokeFactory(
                'Collection',
                id='testcollection',
                title=u'Test Collection',
                query=[{
                    'i': 'portal_type',
                    'o': 'plone.app.querystring.operation.selection.any',
                    'v': ['Document', 'Event']
                }],
            )
            portal.invokeFactory(
                'Event',
                id='testevent',
                title=u'Test Event',
                start=datetime.now() + timedelta(days=1),
                end=datetime.now() + timedelta(days=2),
                subject=[u'Süper', u'Evänt'],
            )
            portal.invokeFactory(
                'Document',
                id='testdoc',
                title=u'Test Document 😉',
                text=RichTextValue(u'Ein heißes Test Dokument'),
                subject=[u'Süper', u'Dokumänt'],
            )
            doc = portal['testdoc']
            # doc.geolocation.latitude = 47.4048832
            # doc.geolocation.longitude = 9.7587760701108
            doc.reindexObject()


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
