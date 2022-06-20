# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from collective.collectionfilter.baseviews import BaseMapsView
from collective.collectionfilter.interfaces import ICollectionMapsSchema
from collective.collectionfilter.portlets import BasePortletRenderer
from plone.app.portlets.portlets import base
from plone.formwidget.geolocation.vocabularies import default_map_layer
from plone.formwidget.geolocation.vocabularies import default_map_layers
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


class ICollectionMapsPortlet(ICollectionMapsSchema, IPortletDataProvider):
    """Portlet interface based on ICollectionMapsSchema"""


@implementer(ICollectionMapsPortlet)
class Assignment(base.Assignment):

    header = u""
    target_collection = None
    view_name = None
    content_selector = "#content-core"
    narrow_down = False
    default_map_layer = default_map_layer
    map_layers = default_map_layers
    geojson_properties_limit = 500

    def __init__(
        self,
        header=u"",
        target_collection=None,
        view_name=None,
        content_selector="#content-core",
        narrow_down=False,
        default_map_layer=default_map_layer,
        map_layers=default_map_layers,
        geojson_properties_limit=500,
    ):
        self.header = header
        self.target_collection = target_collection
        self.view_name = view_name
        self.content_selector = content_selector
        self.narrow_down = narrow_down
        self.default_map_layers = default_map_layers
        self.map_layers = map_layers
        self.geojson_properties_limit = geojson_properties_limit

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return _(u"Collection Maps")


class Renderer(BasePortletRenderer, BaseMapsView):
    render = ViewPageTemplateFile("maps.pt")


class AddForm(base.AddForm):

    schema = ICollectionMapsPortlet
    label = _(u"Add Collection Maps Portlet")
    description = _(u"This portlet allows map filtering in collection results.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    schema = ICollectionMapsPortlet
    label = _(u"Edit Collection Maps Portlet")
    description = _(u"This portlet allows map filtering in collection results.")
