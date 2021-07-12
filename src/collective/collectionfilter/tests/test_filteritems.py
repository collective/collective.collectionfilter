# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest


try:
    from urllib.parse import parse_qs
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse, parse_qs

from collective.collectionfilter.filteritems import get_filter_items
from collective.collectionfilter.query import make_query
from collective.collectionfilter.testing import (  # noqa
    COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING,
)
from collective.collectionfilter.utils import safe_decode
from plone.app.contenttypes.interfaces import ICollection


def get_data_by_val(result, val):
    for r in result:
        if r["value"] == val:
            return r


def is_filter_selected(result, val):
    filter = get_data_by_val(result, val)
    if "selected" in filter["css_class"]:
        return True

    return False


def qs(result, index):
    url = get_data_by_val(result, index)["url"]
    _, _, _, _, query, _ = urlparse(url)
    result = parse_qs(query)
    del result["collectionfilter"]
    # Quick hack to get single values back from being lists
    result.update(dict([(k, v[0]) for k, v in result.items() if len(v) == 1]))
    return safe_decode(result)


class TestFilteritems(unittest.TestCase):

    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.collection = self.portal["testcollection"]
        self.collection_uid = self.collection.UID()

    def assertOption(self, results, option, count, selected=None, title=None, css=None):
        item = get_data_by_val(results, option)
        self.assertIsNotNone(item, u"Filter option not found {option}".format(option=option))
        is_selected = u"selected" if selected else u"unselected"
        self.assertEqual(
            item["count"], count,
            msg=u"Test that the number of results for {} if {} is {} but got {}".format(
                option, is_selected, count, item["count"])
        )
        if title is not None:
            self.assertEqual(item["title"], title)
        if selected is not None:
            self.assertEqual(item["selected"], selected, msg=u"{} should be {} but isn't".format(
                option, is_selected))
        if css is not None:
            self.assertIn(css, item["css_class"].split())

    def assertListingLen(self, results, option, length):
        catalog_results = ICollection(self.collection).results(
            batch=False, brains=True, custom_query=make_query(qs(results, option))
        )
        self.assertEqual(len(catalog_results), length, msg=u"Expected {} listing results, got {}".format(length, len(catalog_results)))

    def test_filteritems(self):
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(self.collection_uid, "Subject", cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertOption(result, u"all", 6, True)
        self.assertOption(result, u"Süper", 2, False)
        self.assertOption(result, u"Evänt", 1, False)
        self.assertOption(result, u"Dokumänt", 2, False)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": u"Süper"},
            cache_enabled=False,
        )

        self.assertEqual(len(result), 4)
        self.assertOption(result, u"Süper", 2, True)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": u"Dokumänt"},
            cache_enabled=False,
        )

        self.assertEqual(len(result), 4)
        self.assertOption(result, u"Dokumänt", 2, True)

        # test narrowed down results
        narrowed_down_result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": u"Dokumänt"},
            narrow_down=True,
            show_count=True,
            cache_enabled=False,
        )

        self.assertEqual(len(narrowed_down_result), 3, msg=u"narrowed result length should be 3")
        # Test that 'Dokumänt' is selected, matching the query
        self.assertOption(narrowed_down_result, u"Dokumänt", 2, True)
        # Test that there are 3 results if unselected
        self.assertOption(narrowed_down_result, u"all", 6, False)

    def test_portal_type_filter(self):
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(
            self.collection_uid, u"portal_type", cache_enabled=False
        )

        self.assertEqual(len(result), 3)
        self.assertOption(result, u"all", 6, True)
        self.assertOption(result, u"Event", 1, False)
        self.assertOption(result, u"Document", 5, False)

        result = get_filter_items(
            self.collection_uid,
            "portal_type",
            request_params={"portal_type": u"Event"},
            cache_enabled=False,
        )

        self.assertEqual(len(result), 3)
        self.assertOption(result, "Event", 1, True)

        # test narrowed down results
        result = get_filter_items(
            self.collection_uid,
            "portal_type",
            request_params={"portal_type": u"Event"},
            narrow_down=True,
            show_count=True,
            cache_enabled=False,
        )

        self.assertEqual(len(result), 2)
        self.assertOption(result, "all", 6, False)
        self.assertOption(result, "Event", 1, True)

        # test operators option on FieldIndex
        result = get_filter_items(
            self.collection_uid,
            "portal_type",
            request_params={
                "portal_type": ["Event", "Document"],
                "portal_type_op": "or",
            },
            filter_type="or",
            cache_enabled=False,
        )

        self.assertEqual(len(result), 3)
        self.assertOption(result, "Event", 1, True)
        self.assertOption(result, "Document", 5, True)

        # and operator is ignored (same result as above)
        result = get_filter_items(
            self.collection_uid,
            "portal_type",
            request_params={
                "portal_type": ["Event", "Document"],
                "portal_type_op": "and",
            },
            filter_type="and",
            cache_enabled=False,
        )

        self.assertEqual(len(result), 3)

    def test_and_filter_type(self):
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(self.collection_uid, "Subject", cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertOption(result, u"all", 6, True)
        self.assertOption(result, u"Süper", 2, False)
        self.assertOption(result, u"Evänt", 1, False)
        self.assertOption(result, u"Dokumänt", 2, False)

        # Test url
        self.assertEqual(qs(result, u"Süper"), {"Subject": u"Süper"})

        self.assertListingLen(result, u"Süper", 2)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": u"Süper"},
            filter_type="and",
            cache_enabled=False,
        )

        self.assertEqual(len(result), 4)
        self.assertOption(result, u"all", 6, False)

        # TODO: I'm not sure these counts are correct. It should represent how many results you will get if you click
        # so should be smaller than this but I guess you need to turn on narrow down for that?
        self.assertOption(result, u"Süper", 2, True)
        self.assertOption(result, u"Evänt", 1, False)
        self.assertOption(result, u"Dokumänt", 2, False)

        self.assertEqual(qs(result, u"Süper"), {})
        self.assertEqual(
            qs(result, u"Dokumänt"),
            {"Subject_op": "and", "Subject": [u"Süper", u"Dokumänt"]},
        )
        self.assertEqual(
            qs(result, u"Evänt"), {"Subject_op": "and", "Subject": [u"Süper", u"Evänt"]}
        )

        # Narrow down by 2
        self.assertListingLen(result, u"Dokumänt", 1)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": [u"Süper", u"Dokumänt"]},
            filter_type="and",
            cache_enabled=False,
        )

        self.assertEqual(len(result), 4)
        self.assertOption(result, u"all", 6, False)
        self.assertOption(result, u"Süper", 2, True)
        self.assertOption(result, u"Dokumänt", 2, True)

        self.assertEqual(qs(result, u"Süper"), {"Subject": u"Dokumänt"})
        self.assertEqual(qs(result, u"Dokumänt"), {"Subject": u"Süper"})
        self.assertEqual(
            qs(result, u"Evänt"),
            {"Subject": [u"Süper", u"Dokumänt", u"Evänt"], "Subject_op": "and"},
        )

        # Clicking on Event we should get 0 results as none will be in common
        self.assertListingLen(result, u"Evänt", 0)

    def test_pathfilter_noquery(self):
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(self.collection_uid, "getPath", cache_enabled=False)

        self.assertEqual(len(result), 3)
        self.assertOption(result, "all", 6, True)
        self.assertOption(result, "testfolder", 2, False, "Test Folder", css="navTreeLevel1")
        self.assertOption(result, "testfolder2", 1, False, "Test Folder2", css="navTreeLevel1")

    def test_pathfilter_level1(self):
        result = get_filter_items(
            self.collection_uid,
            "getPath",
            cache_enabled=False,
            request_params={"path": "testfolder"},
            narrow_down=True
        )
        self.assertEqual(len(result), 3)
        self.assertOption(result, "all", 2, False, "All")
        self.assertOption(result, "testfolder", 2, True, "Test Folder", css="navTreeLevel1")
        self.assertOption(result, "testfolder/testsubfolder", 1, False, "Test Sub-Folder", css="navTreeLevel2")

    def test_pathfilter_level2(self):
        result = get_filter_items(
            self.collection_uid,
            "getPath",
            cache_enabled=False,
            request_params={"path": "testfolder/testsubfolder"},
            narrow_down=True
        )

        self.assertEqual(len(result), 3)
        self.assertOption(result, "all", 1, False, "All")
        self.assertOption(result, "testfolder", 1, True, "Test Folder", css="navTreeLevel1")
        self.assertOption(result, "testfolder/testsubfolder", 1, True, "Test Sub-Folder", css="navTreeLevel2")

    def test_pathfilter_level2_nonarrow(self):
        result = get_filter_items(
            self.collection_uid,
            "getPath",
            cache_enabled=False,
            request_params={"path": "testfolder/testsubfolder"},
            narrow_down=False
        )

        self.assertEqual(len(result), 3)
        self.assertOption(result, "all", 6, False, "All")
        self.assertOption(result, "testfolder", 1, True, "Test Folder", css="navTreeLevel1")
        self.assertOption(result, "testfolder/testsubfolder", 1, True, "Test Sub-Folder", css="navTreeLevel2")
        self.assertOption(result, "testfolder2", 1, False, "Test Folder2", css="navTreeLevel1")

    def test_pathfilter_level1_empty(self):
        result = get_filter_items(
            self.collection_uid,
            "getPath",
            cache_enabled=False,
            request_params={"path": "testfolder2"},
            narrow_down=True
        )

        self.assertEqual(len(result), 2)
        self.assertOption(result, "testfolder2", 1, True, "Test Folder2", css="navTreeLevel1")

    def test_boolean_filter(self):
        """Validate boolean fields are shown with all values."""
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(
            self.collection_uid, "exclude_from_nav", cache_enabled=False
        )

        self.assertEqual(len(result), 3)
        self.assertOption(result, "all", 6, True)
        self.assertOption(result, True, 1, False)
        self.assertOption(result, False, 4, False)

        # test narrowed down results
        narrowed_down_result = get_filter_items(
            self.collection_uid,
            "exclude_from_nav",
            request_params={"exclude_from_nav": True},
            narrow_down=True,
            show_count=True,
            cache_enabled=False,
        )

        self.assertEqual(
            len(narrowed_down_result), 2, msg=u"narrowed result length should be 2"
        )
        # Test that 'Yes' is selected, matching the query
        self.assertOption(narrowed_down_result, True, 1, True)
        # Test that there are 6 results if unselected
        self.assertOption(result, "all", 6, True)

        # test narrowed down results
        narrowed_down_result = get_filter_items(
            self.collection_uid,
            "exclude_from_nav",
            request_params={"exclude_from_nav": False},
            narrow_down=True,
            show_count=True,
            cache_enabled=False,
        )

        self.assertEqual(
            len(narrowed_down_result), 2, msg=u"narrowed result length should be 2"
        )
        # Test that 'No' is selected, matching the query
        self.assertEqual(
            get_data_by_val(narrowed_down_result, False)["selected"],
            True,  # noqa
        )
        self.assertOption(narrowed_down_result, False, 4, True)
        # Test that there are 6 results if unselected",
        self.assertOption(narrowed_down_result, "all", 6, False)
