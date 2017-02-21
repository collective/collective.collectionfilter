from .interfaces import IGroupByCriteria
from .vocabularies import EMPTY_MARKER
from .vocabularies import TEXT_IDX
from Products.CMFPlone.utils import safe_unicode
from zope.component import getUtility


def safe_decode(val):
    """Safely create unicode values.
    """
    ret = val
    if isinstance(val, dict):
        ret = dict([(safe_decode(k), safe_decode(v)) for k, v in val.items()])
    elif isinstance(val, list):
        ret = [safe_decode(it) for it in val]
    elif isinstance(val, tuple):
        ret = (safe_decode(it) for it in val)
    elif val:
        ret = safe_unicode(val)
    return ret


def safe_encode(val):
    """Safely encode a value to utf-8.
    """
    ret = val
    if isinstance(val, dict):
        ret = dict([(safe_encode(k), safe_encode(v)) for k, v in val.items()])
    elif isinstance(val, list):
        ret = [safe_encode(it) for it in val]
    elif isinstance(val, tuple):
        ret = (safe_encode(it) for it in val)
    elif isinstance(val, basestring):
        ret = safe_unicode(val).encode('utf-8')
    return ret


def make_query(params_dict):
    """Make a query from a dictionary of parameters, like a request form.
    """
    query_dict = {}
    groupby_criteria = getUtility(IGroupByCriteria).groupby
    for val in groupby_criteria.values():
        idx = val['index']
        if idx in params_dict:
            crit = params_dict.get(idx) or EMPTY_MARKER
            if idx == 'Subject':
                # Subject does not accept unicode values
                # https://github.com/plone/Products.CMFPlone/issues/470
                crit = safe_encode(crit)
            else:
                crit = safe_decode(crit)
            # filter operator
            op = params_dict.get(idx + '_op', 'or')
            if op not in ['and', 'or']:
                op = 'or'
            # add filter query
            query_dict[idx] = {'operator': op, 'query': crit}

    if TEXT_IDX in params_dict:
        query_dict[TEXT_IDX] = safe_decode(params_dict.get(TEXT_IDX))

    return query_dict
