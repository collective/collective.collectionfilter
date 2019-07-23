# -*- coding: utf-8 -*-
__import__('pkg_resources').declare_namespace(__name__)


try:
    from Products.CMFPlone.utils import get_top_request
except ImportError:
    # to make geolocation compatible we will patch plone
    import Products.CMFPlone.utils
    from collective.collectionfilter.utils import get_top_request
    Products.CMFPlone.utils.get_top_request = get_top_request
