from plone import api
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.utils import safe_unicode


try:
    from plone.app.blocks.layoutbehavior import ILayoutAware
except ImportError:
    ILayoutAware = None


def target_collection_base_path(context):
    for potential_context in context.aq_chain:
        if IFolderish.providedBy(potential_context):
            # Actually makes no sense to pick the collection path as it means you have to go up
            # to pick the collection. Instead the collection should be the default
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
        "collective.collectionfilter.target_collection_types", default=default
    )


def safe_decode(val):
    """Safely create unicode values."""
    if isinstance(val, dict):
        return {
            safe_decode(k): safe_decode(v) for k, v in val.items() if v is not None
        }  # noqa
    if isinstance(val, list):
        return [safe_decode(it) for it in val]
    if isinstance(val, tuple):
        return (safe_decode(it) for it in val)
    if val:
        return safe_unicode(val)
    return val


def safe_encode(val):
    """Safely encode a value to utf-8."""
    if isinstance(val, dict):
        return {
            safe_encode(k): safe_encode(v) for k, v in val.items() if v is not None
        }  # noqa
    if isinstance(val, list):
        return [safe_encode(it) for it in val]
    if isinstance(val, tuple):
        return (safe_encode(it) for it in val)
    if isinstance(val, str):
        return safe_unicode(val).encode("utf-8")
    return val


def safe_iterable(value):
    if value is None:
        return []
    if isinstance(value, str):
        # do not expand a string to a list of chars
        return [value]
    try:
        return list(value)
    except TypeError:
        # int and other stuff
        return [value]


def clean_query(urlquery, ignores):
    """remove all to-be-ignored request parameters."""
    cleaned_query = urlquery.copy()
    for it in ignores:
        # Remove problematic url parameters
        if it in cleaned_query:
            # full match
            del cleaned_query[it]
        else:
            # enhanced partial check
            for urlkey in cleaned_query:
                # also delete prefixed (like with tile id) or
                # postfixed (like :int) keys
                if it in urlkey:
                    del cleaned_query[urlkey]
                    break
    return cleaned_query


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
    urlquery = clean_query(request_params, ignore_params)
    urlquery.update({"collectionfilter": "1"})  # marker
    return urlquery


def get_top_request(request):
    """Get highest request from a subrequest."""

    def _top_request(req):
        parent_request = req.get("PARENT_REQUEST", None)
        return _top_request(parent_request) if parent_request else req

    return _top_request(request)
