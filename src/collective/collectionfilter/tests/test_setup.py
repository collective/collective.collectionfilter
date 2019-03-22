# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.collectionfilter.testing import COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest

no_get_installer = False

try:
    from Products.CMFPlone.utils import get_installer
except Exception:
    no_get_installer = True


class TestSetup(unittest.TestCase):
    """Test that collective.collectionfilter is properly installed."""

    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])

    def test_product_installed(self):
        """Test if collective.collectionfilter is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'collective.collectionfilter'))

    def test_browserlayer(self):
        """Test that ICollectionFilterBrowserLayer is registered."""
        from collective.collectionfilter.interfaces import (
            ICollectionFilterBrowserLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectionFilterBrowserLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstall_product('collective.collectionfilter')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.collectionfilter is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'collective.collectionfilter'))

    def test_browserlayer_removed(self):
        """Test that ICollectionFilterBrowserLayer is removed."""
        from collective.collectionfilter.interfaces import \
            ICollectionFilterBrowserLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            ICollectionFilterBrowserLayer,
            utils.registered_layers())
