# -*- coding: utf-8 -*-
from collective.collectionfilter.interfaces import IGroupByCriteria
from collective.collectionfilter.utils import safe_decode
from collective.collectionfilter.vocabularies import EMPTY_MARKER
from collective.collectionfilter.vocabularies import GEOLOC_IDX
from collective.collectionfilter.vocabularies import TEXT_IDX
from logging import getLogger
from plone import api
from zope.component import getUtility

logger = getLogger('collective.collectionfilter')


def make_query(params_dict):
    """Make a query from a dictionary of parameters, like a request form.
    """
    query_dict = {}
    groupby_criteria = getUtility(IGroupByCriteria).groupby
    cat = api.portal.get_tool('portal_catalog')

    for val in groupby_criteria.values():
        idx = val['index']
        if idx in params_dict:
            crit = params_dict.get(idx) or EMPTY_MARKER
            cat_idx = cat._catalog.indexes.get(idx)

            idx_mod = val.get('index_modifier', None)
            crit = idx_mod(crit) if idx_mod else safe_decode(crit)

            # filter operator
            op = params_dict.get(idx + '_op', None)
            idx_has_operator = 'operator' in getattr(cat_idx, 'query_options', ['query', ])  # noqa: E501

            if op is None or not idx_has_operator:
                # add filter query
                query_dict[idx] = {'query': crit}
            else:
                if op not in ['and', 'or']:
                    op = 'or'
                # add filter query
                query_dict[idx] = {'operator': op, 'query': crit}

    for idx in GEOLOC_IDX:
        if idx in params_dict:
            # lat/lng query has to be float values
            try:
                query_dict[idx] = dict(
                    query=[
                        float(params_dict[idx]['query'][0]),
                        float(params_dict[idx]['query'][1]),
                    ],
                    range=params_dict[idx]['range'])
            except (ValueError, TypeError):
                logger.warning(
                    "Could not apply lat/lng values to filter: %s",
                    params_dict[idx])

    if TEXT_IDX in params_dict and params_dict.get(TEXT_IDX):
        query_dict[TEXT_IDX] = safe_decode(params_dict.get(TEXT_IDX))

    if 'sort_on' in params_dict:
        query_dict['sort_on'] = params_dict['sort_on']
        query_dict['sort_order'] = params_dict.get('sort_order', 'ascending')

    return query_dict
