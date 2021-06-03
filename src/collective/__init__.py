# -*- coding: utf-8 -*-
__import__("pkg_resources").declare_namespace(__name__)


try:
    from Products.CMFPlone.utils import get_top_request
except ImportError:
    # to make geolocation compatible we will patch plone
    from collective.collectionfilter.utils import get_top_request

    import Products.CMFPlone.utils

    Products.CMFPlone.utils.get_top_request = get_top_request
