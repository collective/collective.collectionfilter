from Products.CMFPlone.utils import safe_unicode

import collections


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


def update_nested_dict(d, u):
    """Update a nested dict.
    Solution by Alex Martelli, http://stackoverflow.com/a/3233356/1337474
    """
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update_nested_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d
