# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.collectionfilter.testing import COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.collectionfilter is properly installed."""

    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

    def test_filteritems(self):
        self.assertTrue(True)
