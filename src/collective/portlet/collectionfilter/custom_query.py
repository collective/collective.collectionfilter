from .collectionfilter import GROUPBY_CRITERIA


def set_content_filter(context, event):
    """Set the content filter dictionary on the request, built from request
    parameters to narrow the results of the collection.
    """
    content_filter = {}
    request = event.request
    for val in GROUPBY_CRITERIA.values():
        idx = val['index']
        if idx in request.form:
            content_filter[idx] = request.form.get(idx)
    event.request.set('contentFilter', content_filter)
