"""Setup tests for this package."""

from collective.collectionfilter.filteritems import get_filter_items
from collective.collectionfilter.query import make_query
from collective.collectionfilter.testing import (  # noqa
    COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING,
)
from collective.collectionfilter.utils import safe_decode
from plone.app.contenttypes.interfaces import ICollection
from urllib.parse import parse_qs
from urllib.parse import urlparse

import unittest


def get_data_by_val(result, val):
    for r in result:
        if r["value"] == val:
            return r


def qs(result, index):
    url = get_data_by_val(result, index)["url"]
    _, _, _, _, query, _ = urlparse(url)
    result = parse_qs(query)
    del result["collectionfilter"]
    # Quick hack to get single values back from being lists
    result.update({k: v[0] for k, v in result.items() if len(v) == 1})
    return safe_decode(result)


class TestFilteritems(unittest.TestCase):
    layer = COLLECTIVE_COLLECTIONFILTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.collection = self.portal["testcollection"]
        self.collection_uid = self.collection.UID()

    def test_filteritems(self):
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(self.collection_uid, "Subject", cache_enabled=False)

        self.assertEqual(len(result), 7)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, "all")["selected"], True)
        self.assertEqual(get_data_by_val(result, "Süper")["count"], 2)
        self.assertEqual(get_data_by_val(result, "Evänt")["count"], 1)
        self.assertEqual(get_data_by_val(result, "Dokumänt")["count"], 2)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": "Süper"},
            cache_enabled=False,
        )

        self.assertEqual(len(result), 7)
        self.assertEqual(get_data_by_val(result, "Süper")["selected"], True)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": "Dokumänt"},
            cache_enabled=False,
        )

        self.assertEqual(len(result), 7)
        self.assertEqual(get_data_by_val(result, "Dokumänt")["selected"], True)

        # test narrowed down results
        narrowed_down_result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": "Dokumänt"},
            narrow_down=True,
            show_count=True,
            cache_enabled=False,
        )

        self.assertEqual(
            len(narrowed_down_result), 3, msg="narrowed result length should be 3"
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, "Dokumänt")["selected"],
            True,  # noqa
            msg="Test that 'Dokumänt' is selected, matching the query",
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, "all")["count"],
            6,
            msg="Test that there are 3 results if unselected",
        )

    def test_portal_type_filter(self):
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(
            self.collection_uid, "portal_type", cache_enabled=False
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, "all")["selected"], True)
        self.assertEqual(get_data_by_val(result, "Event")["count"], 1)
        self.assertEqual(get_data_by_val(result, "Document")["count"], 5)

        result = get_filter_items(
            self.collection_uid,
            "portal_type",
            request_params={"portal_type": "Event"},
            cache_enabled=False,
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, "Event")["selected"], True)

        # test narrowed down results
        result = get_filter_items(
            self.collection_uid,
            "portal_type",
            request_params={"portal_type": "Event"},
            narrow_down=True,
            show_count=True,
            cache_enabled=False,
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(
            get_data_by_val(result, "all")["count"],
            6,
            msg="Test that the number of results if unselected is 3",
        )

        self.assertEqual(
            get_data_by_val(result, "Event")["selected"],
            True,
            msg="Test that Event portal_type is selected matching the query",
        )

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
        self.assertEqual(get_data_by_val(result, "Event")["selected"], True)
        self.assertEqual(get_data_by_val(result, "Document")["selected"], True)  # noqa

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

        self.assertEqual(len(result), 7)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, "all")["selected"], True)
        self.assertEqual(get_data_by_val(result, "Süper")["count"], 2)
        self.assertEqual(get_data_by_val(result, "Evänt")["count"], 1)
        self.assertEqual(get_data_by_val(result, "Dokumänt")["count"], 2)

        # Test url
        self.assertEqual(qs(result, "Süper"), {"Subject": "Süper"})

        catalog_results = ICollection(self.collection).results(
            batch=False, brains=True, custom_query=make_query(qs(result, "Süper"))
        )
        self.assertEqual(len(catalog_results), 2)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": "Süper"},
            filter_type="and",
            cache_enabled=False,
        )

        self.assertEqual(len(result), 7)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)

        # TODO: I'm not sure these counts are correct. It should represent how many results you will get if you click
        # so should be smaller than this but I guess you need to turn on narrow down for that?
        self.assertEqual(get_data_by_val(result, "Süper")["count"], 2)
        self.assertEqual(get_data_by_val(result, "Evänt")["count"], 1)
        self.assertEqual(get_data_by_val(result, "Dokumänt")["count"], 2)

        self.assertEqual(get_data_by_val(result, "Süper")["selected"], True)

        self.assertEqual(qs(result, "Süper"), {})
        self.assertEqual(
            qs(result, "Dokumänt"),
            {"Subject_op": "and", "Subject": ["Süper", "Dokumänt"]},
        )
        self.assertEqual(
            qs(result, "Evänt"), {"Subject_op": "and", "Subject": ["Süper", "Evänt"]}
        )

        # Narrow down by 2

        catalog_results = ICollection(self.collection).results(
            batch=False, brains=True, custom_query=make_query(qs(result, "Dokumänt"))
        )
        self.assertEqual(len(catalog_results), 1)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": ["Süper", "Dokumänt"]},
            filter_type="and",
            cache_enabled=False,
        )

        self.assertEqual(len(result), 7)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, "Süper")["count"], 2)

        self.assertEqual(get_data_by_val(result, "Evänt")["count"], 1)
        self.assertEqual(get_data_by_val(result, "Dokumänt")["count"], 2)

        self.assertEqual(get_data_by_val(result, "Süper")["selected"], True)
        self.assertEqual(get_data_by_val(result, "Dokumänt")["selected"], True)

        self.assertEqual(qs(result, "Süper"), {"Subject": "Dokumänt"})
        self.assertEqual(qs(result, "Dokumänt"), {"Subject": "Süper"})
        self.assertEqual(
            qs(result, "Evänt"),
            {"Subject": ["Süper", "Dokumänt", "Evänt"], "Subject_op": "and"},
        )

        # Clicking on Event we should get 0 results as none will be in common
        catalog_results = ICollection(self.collection).results(
            batch=False, brains=True, custom_query=make_query(qs(result, "Evänt"))
        )
        self.assertEqual(len(catalog_results), 0)

    def test_boolean_filter(self):
        """Validate boolean fields are shown with all values."""
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(
            self.collection_uid, "exclude_from_nav", cache_enabled=False
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, "all")["selected"], True)
        self.assertEqual(get_data_by_val(result, True)["count"], 2)
        self.assertEqual(get_data_by_val(result, False)["count"], 4)

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
            len(narrowed_down_result), 2, msg="narrowed result length should be 2"
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, True)["selected"],
            True,  # noqa
            msg="Test that 'Yes' is selected, matching the query",
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, "all")["count"],
            6,
            msg="Test that there are 3 results if unselected",
        )

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
            len(narrowed_down_result), 2, msg="narrowed result length should be 2"
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, False)["selected"],
            True,  # noqa
            msg="Test that 'No' is selected, matching the query",
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, "all")["count"],
            6,
            msg="Test that there are 3 results if unselected",
        )
