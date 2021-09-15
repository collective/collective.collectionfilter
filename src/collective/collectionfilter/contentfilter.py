# -*- coding: utf-8 -*-
from collective.collectionfilter.query import make_query


def set_content_filter(context, event):
    """Set the content filter dictionary on the request, built from request
    parameters to narrow the results of the collection.
    """
    req = event.request
    if "collectionfilter" not in req.form or "contentFilter" in req:
        return
    # We leave collectionfilter=1 in req.form so that it gets put into batch links
    content_filter = make_query(req.form)
    event.request["contentFilter"] = content_filter
