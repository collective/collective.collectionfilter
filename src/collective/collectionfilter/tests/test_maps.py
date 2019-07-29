# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest

from collective.collectionfilter.testing import COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING  # noqa


class TestFilteritems(unittest.TestCase):

    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.collection = self.portal['testcollection']

    def test_locationfilter(self):
        self.assertEqual(len(self.portal['testcollection'].results()), 6)
