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
from plone.testing.zope import WSGI_SERVER_FIXTURE

import json
import os
import pytz


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

        import collective.collectionfilter.tests

        self.loadZCML(package=collective.collectionfilter.tests)

    def setUpPloneSite(self, portal):
        from plone.formwidget.geolocation.geolocation import Geolocation

        applyProfile(portal, "plone.app.mosaic:default")
        applyProfile(portal, "collective.geolocationbehavior:default")
        applyProfile(portal, "collective.collectionfilter:default")
        applyProfile(portal, "collective.collectionfilter.tests:testing")

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
                title="Test Document and Documént",
                text=RichTextValue(
                    "Ein heißes Test Dokument", "text/plain", "text/html"
                ),
                subject=["Süper", "Dokumänt"],
                exclude_from_nav=False,
            )
            portal.invokeFactory(
                "Document",
                id="testdoc2",
                title="Páge",
                text=RichTextValue(
                    "Ein heiBes Test Dokument", "text/plain", "text/html"
                ),
                subject=["Dokumänt"],
                exclude_from_nav=True,
            )
            doc = portal["testdoc"]
            doc.geolocation = Geolocation(47.4048832, 9.7587760701108)
            doc.reindexObject()

            portal.invokeFactory(
                "Folder",
                id="folder1",
                title="Folder with Contentelements",
                exclude_from_nav=False,
            )

            portal.invokeFactory(
                "Collection",
                id="mycollection",
                title="Test Multi Collection",
                query=[
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Document", "Event", "News Item"],
                    },
                    {
                        "i": "path",
                        "o": "plone.app.querystring.operation.string.absolutePath",
                        "v": "{}::-1".format(
                            portal.folder1.UID(),
                        ),
                    },
                ],
            )

            portal.folder1.invokeFactory(
                "Document",
                id="mydoc-red",
                title="Page Red",
                text=RichTextValue(
                    "Page 1 with Subject Red", "text/plain", "text/html"
                ),
                subject=["red"],
                exclude_from_nav=False,
            )

            portal.folder1.invokeFactory(
                "Document",
                id="mydoc-green",
                title="Page Green",
                text=RichTextValue(
                    "Page 2 with Subject Green", "text/plain", "text/html"
                ),
                subject=["green"],
                exclude_from_nav=True,
            )

            portal.folder1.invokeFactory(
                "Document",
                id="mydoc-blue",
                title="Page Blue",
                text=RichTextValue(
                    "Page 3 with Subject Blue", "text/plain", "text/html"
                ),
                subject=["blue"],
                exclude_from_nav=False,
            )

            portal.folder1.invokeFactory(
                "News Item",
                id="newsitem-red",
                title="News Item Red",
                text=RichTextValue(
                    "News Item 1 with Subject Red", "text/plain", "text/html"
                ),
                subject=["red"],
                exclude_from_nav=True,
            )

            portal.folder1.invokeFactory(
                "News Item",
                id="newsitem-blue",
                title="News Item Blue",
                text=RichTextValue(
                    "News Item 2 with Subject Blue", "text/plain", "text/html"
                ),
                subject=["blue"],
                exclude_from_nav=False,
            )

            portal.folder1.invokeFactory(
                "News Item",
                id="newsitem-green",
                title="News Item Green",
                text=RichTextValue(
                    "News Item 3 with Subject Green", "text/plain", "text/html"
                ),
                subject=["green"],
                exclude_from_nav=True,
            )


COLLECTIVE_COLLECTIONFILTER_FIXTURE = CollectiveCollectionFilterLayer()


COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_COLLECTIONFILTER_FIXTURE,),
    name="CollectiveCollectionFilterLayer:IntegrationTesting",
)

COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_COLLECTIONFILTER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="CollectiveCollectionFilterLayer:AcceptanceTesting",
)


class CollectiveCollectionFilterAjaxEnabledLayer(CollectiveCollectionFilterLayer):
    def setUpPloneSite(self, portal):
        _set_ajax_enabled(True)
        os.environ["ROBOT_AJAX_ENABLED"] = "True"
        super().setUpPloneSite(portal)

    def tearDownPloneSite(self, portal):
        super().tearDownPloneSite(portal)
        del os.environ["ROBOT_AJAX_ENABLED"]


AJAX_ENABLED_FIXTURE = CollectiveCollectionFilterAjaxEnabledLayer()
COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED = FunctionalTesting(
    bases=(
        AJAX_ENABLED_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="CollectiveCollectionFilterLayer:AcceptanceTestingPortlet_AjaxEnabled",
)


class CollectiveCollectionFilterAjaxDisabledLayer(CollectiveCollectionFilterLayer):
    def setUpPloneSite(self, portal):
        _set_ajax_enabled(False)
        super().setUpPloneSite(portal)


AJAX_DISABLED_FIXTURE = CollectiveCollectionFilterAjaxDisabledLayer()
COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED = FunctionalTesting(
    bases=(
        AJAX_DISABLED_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="CollectiveCollectionFilterLayer:AcceptanceTestingPortlet_AjaxDisabled",
)


class CollectiveCollectionFilterTilesLayer(CollectiveCollectionFilterLayer):
    def setUpPloneSite(self, portal):
        os.environ["ROBOT_USE_TILES"] = "True"
        super().setUpPloneSite(portal)

    def tearDownPloneSite(self, portal):
        super().tearDownPloneSite(portal)
        del os.environ["ROBOT_USE_TILES"]


TILES_FIXTURE = CollectiveCollectionFilterTilesLayer()
COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_TILES = FunctionalTesting(
    bases=(
        TILES_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="CollectiveCollectionFilterLayer:AcceptanceTesting_Tiles",
)
