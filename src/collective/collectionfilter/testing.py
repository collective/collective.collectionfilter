# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.textfield.value import RichTextValue
from plone.testing import z2
from Products.PluginIndexes.BooleanIndex.BooleanIndex import BooleanIndex

import json
import os
import pytz
import six


def _set_ajax_enabled(should_enable_ajax):
    pattern_options = api.portal.get_registry_record("plone.patternoptions")
    data = {"collectionfilter": str(json.dumps({"ajaxLoad": should_enable_ajax}))}
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
        from plone.formwidget.geolocation.geolocation import Geolocation

        applyProfile(portal, "plone.app.mosaic:default")
        applyProfile(portal, "collective.geolocationbehavior:default")
        applyProfile(portal, "collective.collectionfilter:default")
        applyProfile(portal, "collective.collectionfilter.tests:testing")

        catalog = api.portal.get_tool(name="portal_catalog")
        if "exclude_from_nav" not in catalog.indexes():
            catalog.addIndex(
                "exclude_from_nav",
                BooleanIndex("exclude_from_nav"),
            )

        with api.env.adopt_roles(["Manager"]):
            portal.invokeFactory(
                "Collection",
                id="testcollection",
                title="Test Collection",
                query=[
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Document", "Event"],
                    }
                ],
            )
            if six.PY2:
                now = datetime.now()
            else:
                now = datetime.now(pytz.UTC)

            portal.invokeFactory(
                "Event",
                id="testevent",
                title="Test Event",
                start=now + timedelta(days=1),
                end=now + timedelta(days=2),
                subject=["Süper", "Evänt"],
                exclude_from_nav=False,
            )
            portal.invokeFactory(
                "Document",
                id="testdoc",
                title="Test Document and Document 😉",
                text=RichTextValue(
                    "Ein heißes Test Dokument", "text/plain", "text/html"
                ),
                subject=["Süper", "Dokumänt"],
                exclude_from_nav=False,
            )
            portal.invokeFactory(
                "Document",
                id="testdoc2",
                title="Page 😉",
                text=RichTextValue(
                    "Ein heiBes Test Dokument", "text/plain", "text/html"
                ),
                subject=["Dokumänt"],
                exclude_from_nav=True,
            )
            doc = portal["testdoc"]
            doc.geolocation = Geolocation(47.4048832, 9.7587760701108)
            doc.reindexObject()


COLLECTIVE_COLLECTIONFILTER_FIXTURE = CollectiveCollectionFilterLayer()


COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_COLLECTIONFILTER_FIXTURE,),
    name="CollectiveCollectionFilterLayer:IntegrationTesting",
)

COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_COLLECTIONFILTER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CollectiveCollectionFilterLayer:AcceptanceTesting",
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
    name="CollectiveCollectionFilterLayer:AcceptanceTestingPortlet_AjaxEnabled",
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
    name="CollectiveCollectionFilterLayer:AcceptanceTestingPortlet_AjaxDisabled",
)


class CollectiveCollectionFilterTilesLayer(CollectiveCollectionFilterLayer):
    def setUpPloneSite(self, portal):
        os.environ["ROBOT_USE_TILES"] = "True"
        super(CollectiveCollectionFilterTilesLayer, self).setUpPloneSite(portal)

    def tearDownPloneSite(self, portal):
        super(CollectiveCollectionFilterTilesLayer, self).tearDownPloneSite(portal)
        del os.environ["ROBOT_USE_TILES"]


TILES_FIXTURE = CollectiveCollectionFilterTilesLayer()
COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_TILES = FunctionalTesting(
    bases=(
        TILES_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CollectiveCollectionFilterLayer:AcceptanceTesting_Tiles",
)
