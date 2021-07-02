# -*- coding: utf-8 -*-
from plone import api
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.utils import safe_unicode
try:
    from plone.app.blocks.layoutbehavior import ILayoutAware
except ImportError:
    ILayoutAware = None
import six


def target_collection_base_path(context):
    for potential_context in context.aq_chain:
        if IFolderish.providedBy(potential_context):
            # Actually makes no sense to pick the collection path as it means you have to go up
            # to pick teh collection. Instead the collection should be the default
            #    or
            # ISyndicatableCollection.providedBy(potential_context
            #                                   )
            context = potential_context
            break
    return "/".join(context.getPhysicalPath())


def target_collection_types(context):
    if ILayoutAware:
        default = ["Collection", "Page", "Folder"]
    else:
        default = ["Collection"]
    return api.portal.get_registry_record(
        "collective.collectionfilter.target_collection_types",
        default=default
    )


def safe_decode(val):
    """Safely create unicode values."""
    ret = val
    if isinstance(val, dict):
        ret = dict(
            [(safe_decode(k), safe_decode(v)) for k, v in val.items() if v is not None]
        )  # noqa
    elif isinstance(val, list):
        ret = [safe_decode(it) for it in val]
    elif isinstance(val, tuple):
        ret = (safe_decode(it) for it in val)
    elif val:
        ret = safe_unicode(val)
    return ret


def safe_encode(val):
    """Safely encode a value to utf-8."""
    ret = val
    if isinstance(val, dict):
        ret = dict(
            [(safe_encode(k), safe_encode(v)) for k, v in val.items() if v is not None]
        )  # noqa
    elif isinstance(val, list):
        ret = [safe_encode(it) for it in val]
    elif isinstance(val, tuple):
        ret = (safe_encode(it) for it in val)
    elif isinstance(val, six.string_types):
        ret = safe_unicode(val).encode("utf-8")
    return ret


def safe_iterable(value):
    if value is None:
        return []
    if isinstance(value, six.string_types):
        # do not expand a string to a list of chars
        return [
            value,
        ]
    else:
        try:
            return list(value)
        except TypeError:
            # int and other stuff
            return [
                value,
            ]
    # could not convert
    return []


def base_query(request_params={}, extra_ignores=[]):
    """Construct base url query."""

    # Defaults
    request_params = request_params or {}
    extra_ignores = extra_ignores or []

    # These request params should be ignored.
    ignore_params = [
        "b_start",
        "b_size",
        "batch",
        "limit",
        "portlethash",
    ] + extra_ignores
    # Now remove all to-be-ignored request parameters.
    urlquery = {k: v for k, v in list(request_params.items()) if k not in ignore_params}
    urlquery.update({"collectionfilter": "1"})  # marker
    return urlquery


def get_top_request(request):
    """Get highest request from a subrequest."""

    def _top_request(req):
        parent_request = req.get("PARENT_REQUEST", None)
        return _top_request(parent_request) if parent_request else req

    return _top_request(request)
