from .collectionfilter import GROUPBY_CRITERIA
from Products.CMFPlone.utils import safe_unicode


def set_content_filter(context, event):
    """Set the content filter dictionary on the request, built from request
    parameters to narrow the results of the collection.
    """
    content_filter = {}
    request = event.request
    for val in GROUPBY_CRITERIA.values():
        idx = val['index']
        if idx in request.form:
            content_filter[idx] = safe_unicode(request.form.get(idx))
    event.request['contentFilter'] = content_filter
