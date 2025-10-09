"""Setup tests for this package."""

from collective.collectionfilter.testing import INTEGRATION_TESTING

import unittest


class TestMaps(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.collection = self.portal["testcollection"]

    def test_locationfilter(self):
        self.assertEqual(len(self.portal["testcollection"].results()), 6)
