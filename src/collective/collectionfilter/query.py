# -*- coding: utf-8 -*-
from collective.collectionfilter.interfaces import IGroupByCriteria
from collective.collectionfilter.utils import safe_decode
from collective.collectionfilter.vocabularies import EMPTY_MARKER
from collective.collectionfilter.vocabularies import GEOLOC_IDX
from collective.collectionfilter.vocabularies import TEXT_IDX
from logging import getLogger
from plone import api
from Products.CMFPlone.browser.search import BAD_CHARS
from Products.CMFPlone.browser.search import quote_chars
from zope.component import getUtility
import plone.api


try:
    from Products.CMFPlone.browser.search import quote
except ImportError:
    # This fix was not in Plone 5.0.x
    def quote(term):
        # The terms and, or and not must be wrapped in quotes to avoid
        # being parsed as logical query atoms.
        if term.lower() in ("and", "or", "not"):
            term = '"%s"' % term
        return term


logger = getLogger("collective.collectionfilter")
ENCODED_BAD_CHARS = safe_decode(BAD_CHARS)


def sanitise_search_query(query):
    for char in ENCODED_BAD_CHARS:
        query = query.replace(char, " ")
    clean_query = [quote(token) for token in query.split()]
    clean_query = quote_chars(clean_query)
    return u" ".join(clean_query)


def make_query(params_dict):
    """Make a query from a dictionary of parameters, like a request form."""
    query_dict = {}
    groupby_criteria = getUtility(IGroupByCriteria).groupby
    cat = api.portal.get_tool("portal_catalog")

    for val in groupby_criteria.values():
        idx = val["index"]
        if idx in params_dict:
            crit = params_dict.get(idx) or EMPTY_MARKER
            cat_idx = cat._catalog.indexes.get(idx)

            idx_mod = val.get("index_modifier", None)
            crit = idx_mod(crit) if idx_mod else safe_decode(crit)

            # filter operator
            op = params_dict.get(idx + "_op", None)
            idx_has_operator = "operator" in getattr(
                cat_idx,
                "query_options",
                [
                    "query",
                ],
            )  # noqa: E501

            if op is None or not idx_has_operator:
                # add filter query
                query_dict[idx] = {"query": crit}
            else:
                if op not in ["and", "or"]:
                    op = "or"
                # add filter query
                query_dict[idx] = {"operator": op, "query": crit}

    for idx in GEOLOC_IDX:
        if idx in params_dict:
            # lat/lng query has to be float values
            try:
                query_dict[idx] = dict(
                    query=[
                        float(params_dict[idx]["query"][0]),
                        float(params_dict[idx]["query"][1]),
                    ],
                    range=params_dict[idx]["range"],
                )
            except (ValueError, TypeError):
                logger.warning(
                    "Could not apply lat/lng values to filter: %s", params_dict[idx]
                )

    if TEXT_IDX in params_dict and params_dict.get(TEXT_IDX):
        safe_text = safe_decode(params_dict.get(TEXT_IDX))
        clean_searchable_text = sanitise_search_query(safe_text)
        query_dict[TEXT_IDX] = clean_searchable_text

    if "sort_on" in params_dict:
        query_dict["sort_on"] = params_dict["sort_on"]
        query_dict["sort_order"] = params_dict.get("sort_order", "ascending")

    # Filter by path if passed in
    if 'path' in params_dict:
        additional_paths = params_dict['path'].split('/')
        query_dict['path'] = {'query': '/'.join(
            list(plone.api.portal.get().getPhysicalPath()) + additional_paths)}

    return query_dict
