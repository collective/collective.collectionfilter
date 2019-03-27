# -*- coding: utf-8 -*-
from collective.geolocationbehavior.geolocation import IGeolocatable
from plone.indexer.decorator import indexer


@indexer(IGeolocatable)
def latitude(obj):
    return obj.geolocation.latitude


@indexer(IGeolocatable)
def longitude(obj):
    return obj.geolocation.longitude
