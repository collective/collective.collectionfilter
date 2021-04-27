# -*- coding: utf-8 -*-
from collective.collectionfilter.baseviews import BaseMapsView
from collective.collectionfilter.interfaces import ICollectionMapsSchema
from collective.collectionfilter.tiles import BaseFilterTile
from plone.supermodel.model import Schema
from Products.CMFPlone.resources import add_bundle_on_request
from Products.CMFPlone.utils import get_top_request
from zope.interface import implementer


class IMapsTile(Schema, ICollectionMapsSchema):
    """ schema for maps tile """


@implementer(IMapsTile)
class MapsTile(BaseFilterTile, BaseMapsView):
    def __init__(self, context, request):
        super(MapsTile, self).__init__(context, request)
        # TODO: does not work, because CMFPlone.resources.browser.resource is
        #       called before this one; subrequest problem
        top_request = get_top_request(request)
        add_bundle_on_request(top_request, "bundle-leaflet")
