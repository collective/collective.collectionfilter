# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest


try:
    from urllib.parse import parse_qs
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse, parse_qs

from collective.collectionfilter.filteritems import (
    get_filter_items,
    get_section_filter_items,
)
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

    def test_filteritems(self):
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(self.collection_uid, "Subject", cache_enabled=False)

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, "all")["selected"], True)
        self.assertEqual(get_data_by_val(result, u"Süper")["count"], 2)
        self.assertEqual(get_data_by_val(result, u"Evänt")["count"], 1)
        self.assertEqual(get_data_by_val(result, u"Dokumänt")["count"], 2)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": u"Süper"},
            cache_enabled=False,
        )

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, u"Süper")["selected"], True)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": u"Dokumänt"},
            cache_enabled=False,
        )

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, u"Dokumänt")["selected"], True)

        # test narrowed down results
        narrowed_down_result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": u"Dokumänt"},
            narrow_down=True,
            show_count=True,
            cache_enabled=False,
        )

        self.assertEqual(
            len(narrowed_down_result), 3, msg=u"narrowed result length should be 3"
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, u"Dokumänt")["selected"],
            True,  # noqa
            msg=u"Test that 'Dokumänt' is selected, matching the query",
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, u"all")["count"],
            6,
            msg=u"Test that there are 3 results if unselected",
        )

    def test_portal_type_filter(self):
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(
            self.collection_uid, "portal_type", cache_enabled=False
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, "all")["selected"], True)
        self.assertEqual(get_data_by_val(result, u"Event")["count"], 1)
        self.assertEqual(get_data_by_val(result, u"Document")["count"], 5)

        result = get_filter_items(
            self.collection_uid,
            "portal_type",
            request_params={"portal_type": u"Event"},
            cache_enabled=False,
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, u"Event")["selected"], True)

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
        self.assertEqual(
            get_data_by_val(result, u"all")["count"],
            6,
            msg=u"Test that the number of results if unselected is 6",
        )

        self.assertEqual(
            get_data_by_val(result, u"Event")["selected"],
            True,
            msg=u"Test that Event portal_type is selected matching the query",
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
        self.assertEqual(get_data_by_val(result, u"Event")["selected"], True)
        self.assertEqual(get_data_by_val(result, u"Document")["selected"], True)  # noqa

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
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, "all")["selected"], True)
        self.assertEqual(get_data_by_val(result, u"Süper")["count"], 2)
        self.assertEqual(get_data_by_val(result, u"Evänt")["count"], 1)
        self.assertEqual(get_data_by_val(result, u"Dokumänt")["count"], 2)

        # Test url
        self.assertEqual(qs(result, u"Süper"), {"Subject": u"Süper"})

        catalog_results = ICollection(self.collection).results(
            batch=False, brains=True, custom_query=make_query(qs(result, u"Süper"))
        )
        self.assertEqual(len(catalog_results), 2)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": u"Süper"},
            filter_type="and",
            cache_enabled=False,
        )

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)

        # TODO: I'm not sure these counts are correct. It should represent how many results you will get if you click
        # so should be smaller than this but I guess you need to turn on narrow down for that?
        self.assertEqual(get_data_by_val(result, u"Süper")["count"], 2)
        self.assertEqual(get_data_by_val(result, u"Evänt")["count"], 1)
        self.assertEqual(get_data_by_val(result, u"Dokumänt")["count"], 2)

        self.assertEqual(get_data_by_val(result, u"Süper")["selected"], True)

        self.assertEqual(qs(result, u"Süper"), {})
        self.assertEqual(
            qs(result, u"Dokumänt"),
            {"Subject_op": "and", "Subject": [u"Süper", u"Dokumänt"]},
        )
        self.assertEqual(
            qs(result, u"Evänt"), {"Subject_op": "and", "Subject": [u"Süper", u"Evänt"]}
        )

        # Narrow down by 2

        catalog_results = ICollection(self.collection).results(
            batch=False, brains=True, custom_query=make_query(qs(result, u"Dokumänt"))
        )
        self.assertEqual(len(catalog_results), 1)

        result = get_filter_items(
            self.collection_uid,
            "Subject",
            request_params={"Subject": [u"Süper", u"Dokumänt"]},
            filter_type="and",
            cache_enabled=False,
        )

        self.assertEqual(len(result), 4)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, u"Süper")["count"], 2)

        self.assertEqual(get_data_by_val(result, u"Evänt")["count"], 1)
        self.assertEqual(get_data_by_val(result, u"Dokumänt")["count"], 2)

        self.assertEqual(get_data_by_val(result, u"Süper")["selected"], True)
        self.assertEqual(get_data_by_val(result, u"Dokumänt")["selected"], True)

        self.assertEqual(qs(result, u"Süper"), {"Subject": u"Dokumänt"})
        self.assertEqual(qs(result, u"Dokumänt"), {"Subject": u"Süper"})
        self.assertEqual(
            qs(result, u"Evänt"),
            {"Subject": [u"Süper", u"Dokumänt", u"Evänt"], "Subject_op": "and"},
        )

        # Clicking on Event we should get 0 results as none will be in common
        catalog_results = ICollection(self.collection).results(
            batch=False, brains=True, custom_query=make_query(qs(result, u"Evänt"))
        )
        self.assertEqual(len(catalog_results), 0)

    def test_sectionfilter(self):
        def is_filter_selected(result, val):
            filter = get_data_by_val(result, val)
            if "selected" in filter["css_class"]:
                return True

            return False

        self.assertEqual(len(self.collection.results()), 6)

        result_all = get_section_filter_items(
            self.collection_uid, "", cache_enabled=False, request_params=None
        )

        self.assertEqual(len(result_all), 3)
        self.assertEqual(get_data_by_val(result_all, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result_all, "all")["level"], 0)
        self.assertEqual(get_data_by_val(result_all, "all")["title"], "Home")
        self.assertEqual(is_filter_selected(result_all, "all"), True)
        self.assertEqual(get_data_by_val(result_all, "testfolder")["count"], 2)
        self.assertEqual(get_data_by_val(result_all, "testfolder")["level"], 1)
        self.assertEqual(
            get_data_by_val(result_all, "testfolder")["title"], "Test Folder"
        )
        self.assertEqual(is_filter_selected(result_all, "testfolder"), False)
        self.assertEqual(get_data_by_val(result_all, "testfolder2")["count"], 1)
        self.assertEqual(get_data_by_val(result_all, "testfolder2")["level"], 1)
        self.assertEqual(
            get_data_by_val(result_all, "testfolder2")["title"], "Test Folder2"
        )
        self.assertEqual(is_filter_selected(result_all, "testfolder2"), False)

        result_folder = get_section_filter_items(
            self.collection_uid,
            "",
            cache_enabled=False,
            request_params={"path": "testfolder"},
        )

        # Todo: Bug causing empty section filter to display.
        # self.assertEqual(len(result_folder), 3)
        self.assertEqual(is_filter_selected(result_folder, "testfolder"), True)

        result_subfolder = get_section_filter_items(
            self.collection_uid,
            "",
            cache_enabled=False,
            request_params={"path": "testfolder/testsubfolder"},
        )

        self.assertEqual(len(result_subfolder), 3)
        self.assertEqual(
            get_data_by_val(result_subfolder, "testsubfolder")["level"], 2
        )
        self.assertEqual(
            is_filter_selected(result_subfolder, "testsubfolder"), True
        )

        result_folder2 = get_section_filter_items(
            self.collection_uid,
            "",
            cache_enabled=False,
            request_params={"path": "testfolder2"},
        )

        self.assertEqual(len(result_folder2), 2)
        self.assertEqual(
            is_filter_selected(result_folder2, "testfolder2"), True
        )

    def test_boolean_filter(self):
        """Validate boolean fields are shown with all values."""
        self.assertEqual(len(self.collection.results()), 6)

        result = get_filter_items(
            self.collection_uid, "exclude_from_nav", cache_enabled=False
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(get_data_by_val(result, "all")["count"], 6)
        self.assertEqual(get_data_by_val(result, "all")["selected"], True)
        self.assertEqual(get_data_by_val(result, True)["count"], 1)
        self.assertEqual(get_data_by_val(result, False)["count"], 5)

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
        self.assertEqual(
            get_data_by_val(narrowed_down_result, True)["selected"],
            True,  # noqa
            msg=u"Test that 'Yes' is selected, matching the query",
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, u"all")["count"],
            6,
            msg=u"Test that there are 6 results if unselected",
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
            len(narrowed_down_result), 2, msg=u"narrowed result length should be 2"
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, False)["selected"],
            True,  # noqa
            msg=u"Test that 'No' is selected, matching the query",
        )
        self.assertEqual(
            get_data_by_val(narrowed_down_result, u"all")["count"],
            6,
            msg=u"Test that there are 6 results if unselected",
        )
