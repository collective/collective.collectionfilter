# -*- coding: utf-8 -*-
from collective.collectionfilter import _
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@provider(IVocabularyFactory)
def MapLayers(context):
    """Vocabulary for available Leaflet map layers.
    For a full list, see:
    http://leaflet-extras.github.io/leaflet-providers/preview/
    """
    items = [
        (_('OpenStreetMap.Mapnik'),           'OpenStreetMap.Mapnik'),
        (_('OpenStreetMap.BlackAndWhite'),    'OpenStreetMap.BlackAndWhite'),
        (_('OpenStreetMap.DE'),               'OpenStreetMap.DE'),
        (_('OpenStreetMap.France'),           'OpenStreetMap.France'),
        (_('Thunderforest.OpenCycleMap'),     'Thunderforest.OpenCycleMap'),
        (_('Thunderforest.Transport'),        'Thunderforest.Transport'),
        (_('Thunderforest.TransportDark'),    'Thunderforest.TransportDark'),
        (_('Thunderforest.Outdoors'),         'Thunderforest.Outdoors'),
        (_('Stamen.Toner'),                   'Stamen.Toner'),
        (_('Stamen.TonerBackground'),         'Stamen.TonerBackground'),
        (_('Stamen.TonerLite'),               'Stamen.TonerLite'),
        (_('Stamen.Watercolor'),              'Stamen.Watercolor'),
        (_('Stamen.Terrain'),                 'Stamen.Terrain'),
        (_('Stamen.TerrainBackground'),       'Stamen.TerrainBackground'),
        (_('Stamen.TopOSMRelief'),            'Stamen.TopOSMRelief'),
        (_('Esri.WorldStreetMap'),            'Esri.WorldStreetMap'),
        (_('Esri.DeLorme'),                   'Esri.DeLorme'),
        (_('Esri.WorldTopoMap'),              'Esri.WorldTopoMap'),
        (_('Esri.WorldImagery'),              'Esri.WorldImagery'),
        (_('Esri.WorldTerrain'),              'Esri.WorldTerrain'),
        (_('Esri.WorldShadedRelief'),         'Esri.WorldShadedRelief'),
        (_('Esri.WorldPhysical'),             'Esri.WorldPhysical'),
        (_('Esri.OceanBasemap'),              'Esri.OceanBasemap'),
        (_('Esri.NatGeoWorldMap'),            'Esri.NatGeoWorldMap'),
        (_('Esri.WorldGrayCanvas'),           'Esri.WorldGrayCanvas'),
        (_('CartoDB.DarkMatter'),             'CartoDB.DarkMatter'),
        (_('CartoDB.DarkMatterNoLabels'),     'CartoDB.DarkMatterNoLabels'),
        (_('NASAGIBS.ViirsEarthAtNight2012'), 'NASAGIBS.ViirsEarthAtNight2012'),  # noqa
    ]
    items = [SimpleTerm(title=i[0], value=i[1]) for i in items]
    return SimpleVocabulary(items)
