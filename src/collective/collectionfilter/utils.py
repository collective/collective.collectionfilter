# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.utils import safe_unicode
import six


def target_collection_base_path(context):
    for potential_context in context.aq_chain:
        if (
            IFolderish.providedBy(potential_context) or
            ISyndicatableCollection.providedBy(potential_context)
        ):
            context = potential_context
            break
    return '/'.join(context.getPhysicalPath())


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
    elif isinstance(val, six.string_types):
        ret = safe_unicode(val).encode('utf-8')
    return ret


def base_query(request_params={}, extra_ignores=[]):
    """Construct base url query.
    """

    # Defaults
    request_params = request_params or {}
    extra_ignores = extra_ignores or []

    # These request params should be ignored.
    ignore_params = [
        'b_start',
        'b_size',
        'batch',
        'sort_on',
        'limit',
        'portlethash'
    ] + extra_ignores
    # Now remove all to-be-ignored request parameters.
    urlquery = {
        k: v for k, v in list(request_params.items()) if k not in ignore_params
    }
    urlquery.update({'collectionfilter': '1'})  # marker
    return urlquery
