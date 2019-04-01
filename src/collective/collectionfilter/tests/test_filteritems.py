# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest

from collective.collectionfilter.testing import COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING  # noqa
from collective.collectionfilter.filteritems import get_filter_items


def get_data_by_val(result, val):
    for r in result:
        if r['value'] == val:
            return r


class TestFilteritems(unittest.TestCase):

    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.collection = self.portal['testcollection']
        self.collection_uid = self.collection.UID()

    def test_filteritems(self):
        self.assertEqual(len(self.collection.results()), 2)

        result = get_filter_items(
            self.collection_uid, 'Subject', cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, 'all')['count'], 2)
        self.assertEqual(get_data_by_val(result, 'all')['selected'], True)
        self.assertEqual(get_data_by_val(result, u'Süper')['count'], 2)
        self.assertEqual(get_data_by_val(result, u'Evänt')['count'], 1)
        self.assertEqual(get_data_by_val(result, u'Dokumänt')['count'], 1)

        result = get_filter_items(
            self.collection_uid, 'Subject',
            request_params={'Subject': u'Süper'},
            cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, u'Süper')['selected'], True)

        result = get_filter_items(
            self.collection_uid, 'Subject',
            request_params={'Subject': u'Dokumänt'},
            cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, u'Dokumänt')['selected'], True)  # noqa

        # test narrowed down results
        result = get_filter_items(
            self.collection_uid, 'Subject',
            request_params={'Subject': u'Dokumänt'},
            narrow_down=True,
            cache_enabled=False)

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, u'Dokumänt')['selected'], True)  # noqa
        self.assertEqual(get_data_by_val(result, u'all')['count'], 1)

    def test_portal_type_filter(self):
        self.assertEqual(len(self.portal['testcollection'].results()), 2)

        result = get_filter_items(
            self.collection_uid, 'portal_type', cache_enabled=False)

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, 'all')['count'], 2)
        self.assertEqual(get_data_by_val(result, 'all')['selected'], True)
        self.assertEqual(get_data_by_val(result, u'Event')['count'], 1)
        self.assertEqual(get_data_by_val(result, u'Document')['count'], 1)

        result = get_filter_items(
            self.collection_uid, 'portal_type',
            request_params={'portal_type': u'Event'},
            cache_enabled=False)

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, u'Event')['selected'], True)

        result = get_filter_items(
            self.collection_uid, 'portal_type',
            request_params={'portal_type': u'Event'},
            narrow_down=True,
            cache_enabled=False)

        self.assertEqual(len(result), 2)
        self.assertEqual(get_data_by_val(result, u'all')['count'], 1)
        self.assertEqual(get_data_by_val(result, u'Event')['selected'], True)