# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest

from collective.collectionfilter.testing import COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING  # noqa
from collective.collectionfilter.filteritems import get_filter_items
from datetime import datetime
from datetime import timedelta
from plone import api
from plone.app.textfield.value import RichTextValue


class TestFilteritems(unittest.TestCase):

    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

        with api.env.adopt_roles(['Manager']):
            self.portal.invokeFactory(
                'Collection',
                id='testcollection',
                title=u'Test Collection',
                query=[{
                    'i': 'portal_type',
                    'o': 'plone.app.querystring.operation.selection.any',
                    'v': ['Document', 'Event']
                }],
            )
            self.portal.invokeFactory(
                'Event',
                id='testevent',
                title=u'Test Event',
                start=datetime.now() + timedelta(days=1),
                end=datetime.now() + timedelta(days=2),
                subject=[u'Süper', u'Evänt'],
            )
            self.portal.invokeFactory(
                'Document',
                id='testdoc',
                title=u'Test Document',
                text=RichTextValue(u'Ein heißes Test Dokument'),
                subject=[u'Süper', u'Dokumänt'],
            )

        self.collection_uid = self.portal['testcollection'].UID()

    def test_filteritems(self):
        self.assertEqual(len(self.portal['testcollection'].results()), 2)

        def _get_data_by_val(result, val):
            for r in result:
                if r['value'] == val:
                    return r

        result = get_filter_items(
            self.collection_uid, 'Subject', cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(_get_data_by_val(result, 'all')['count'], 2)
        self.assertEqual(_get_data_by_val(result, 'all')['selected'], True)
        self.assertEqual(_get_data_by_val(result, u'Süper')['count'], 2)
        self.assertEqual(_get_data_by_val(result, u'Evänt')['count'], 1)
        self.assertEqual(_get_data_by_val(result, u'Dokumänt')['count'], 1)

        result = get_filter_items(
            self.collection_uid, 'Subject',
            request_params={'Subject': u'Süper'},
            cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(_get_data_by_val(result, u'Süper')['selected'], True)

        result = get_filter_items(
            self.collection_uid, 'Subject',
            request_params={'Subject': u'Dokumänt'},
            cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(_get_data_by_val(result, u'Dokumänt')['selected'], True)  # noqa

        # test narrowed down results
        result = get_filter_items(
            self.collection_uid, 'Subject',
            request_params={'Subject': u'Dokumänt'},
            narrow_down=True,
            cache_enabled=False)

        self.assertEqual(len(result), 3)
        self.assertEqual(_get_data_by_val(result, u'Dokumänt')['selected'], True)  # noqa
        self.assertEqual(_get_data_by_val(result, u'all')['count'], 1)
