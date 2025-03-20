"""Setup tests for this package."""

from collective.collectionfilter.testing import (  # noqa
    COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import login

import unittest
from plone.app.testing import setRoles, TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from collective.collectionfilter.tiles.filter import FilterTile


class TestFilteritems(unittest.TestCase):
    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.page = api.content.create(
            container=self.portal,
            type="Document",
            id="page",
        )

    def test_editor_role_can_render_filtertile(self):
        setRoles(self.portal, TEST_USER_ID, ["Editor"])
        tile = FilterTile(self.page, self.request)
        tile.__name__ = 'collective.collectionfilter.tiles.filter.FilterTile'
        tile.context = self.page
        self.assertTrue(tile.edit_url.startswith('http://nohost/plone/page/@@edit-tile/'))
