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
import transaction
import json

try:
    # Python 2: "unicode" is built-in
    unicode
except NameError:
    unicode = str


def _set_ajax_enabled(should_enable_ajax):
    pattern_options = api.portal.get_registry_record("plone.patternoptions")
    data = {"collectionfilter": unicode(json.dumps({"ajaxLoad": should_enable_ajax}))}
    pattern_options.update(data)
    api.portal.set_registry_record("plone.patternoptions", pattern_options)


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
            portal.invokeFactory(
                'Document',
                id='testdoc2',
                title=u'Page 😉',
                text=RichTextValue(u'Ein heißes Test Dokument'),
                subject=[u'Dokumänt'],
            )
            portal.invokeFactory(
                'Folder',
                id='testfolder',
                title=u'Test Folder',
            )
            portal.invokeFactory(
                'Folder',
                id='testfolder2',
                title=u'Test Folder2',
            )
            portal.invokeFactory(
                'Folder',
                id='testfolder3',
                title=u'Test Folder3',
            )
            portal.testfolder.invokeFactory(
                'Document',
                id=u'testsubdoc',
                title=u'Test Folder Document',
            )
            portal.testfolder.invokeFactory(
                'Folder',
                id=u'testsubfolder',
                title=u'Test Sub-Folder',
            )
            portal.testfolder.testsubfolder.invokeFactory(
                'Document',
                id=u'testsubsubdoc',
                title=u'Test Sub-Folder Document',
            )
            portal.testfolder2.invokeFactory(
                'Document',
                id=u'testsubdoc2',
                title=u'Test Folder2 Document',
            )
            doc = portal['testdoc']
            # doc.geolocation.latitude = 47.4048832
            # doc.geolocation.longitude = 9.7587760701108
            doc.reindexObject()

            transaction.commit()


COLLECTIVE_COLLECTIONFILTER_FIXTURE = CollectiveCollectionFilterLayer()


COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_COLLECTIONFILTER_FIXTURE,),
    name='CollectiveCollectionFilterLayer:IntegrationTesting',
)

COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_COLLECTIONFILTER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveCollectionFilterLayer:AcceptanceTesting',
)


class CollectiveCollectionFilterAjaxEnabledLayer(CollectiveCollectionFilterLayer):
    def setUpPloneSite(self, portal):
        _set_ajax_enabled(True)
        super(CollectiveCollectionFilterAjaxEnabledLayer, self).setUpPloneSite(portal)

AJAX_ENABLED_FIXTURE = CollectiveCollectionFilterAjaxEnabledLayer()
COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED = FunctionalTesting(
    bases=(
        AJAX_ENABLED_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveCollectionFilterLayer:AcceptanceTesting_AjaxEnabled',
)


class CollectiveCollectionFilterAjaxDisabledLayer(CollectiveCollectionFilterLayer):
    def setUpPloneSite(self, portal):
        _set_ajax_enabled(False)
        super(CollectiveCollectionFilterAjaxDisabledLayer, self).setUpPloneSite(portal)


AJAX_DISABLED_FIXTURE = CollectiveCollectionFilterAjaxDisabledLayer()
COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED = FunctionalTesting(
    bases=(
        AJAX_DISABLED_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveCollectionFilterLayer:AcceptanceTesting_AjaxDisabled',
)
