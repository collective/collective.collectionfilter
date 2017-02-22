# -*- coding: utf-8 -*-
from .query import make_query


def set_content_filter(context, event):
    """Set the content filter dictionary on the request, built from request
    parameters to narrow the results of the collection.
    """
    content_filter = make_query(event.request.form)
    event.request['contentFilter'] = content_filter
