# collective.collectionfilter

[![CI](https://github.com/collective/collective.collectionfilter/actions/workflows/test-matrix.yml/badge.svg)](https://github.com/collective/collective.collectionfilter/actions/workflows/test-matrix.yml)
[![Meta](https://github.com/collective/collective.collectionfilter/actions/workflows/meta.yml/badge.svg)](https://github.com/collective/collective.collectionfilter/actions/workflows/meta.yml)

Faceted navigation filter for collection or contentlisting tiles.

Filter listing results for any catalog-indexed field — subjects, authors, portal types, and more.
The available filter types can be extended (see `collective.collectionfilter.vocabularies`).

There are five portlets/tiles available:

- **Collection Filter** — filter by values (select, radio, checkbox, link)
- **Collection Search** — fulltext search (SearchableText) on collection results
- **Collection Maps** — a [LeafletJS](https://leafletjs.com/) map that shows and filters `IGeolocatable` items (requires `collective.geolocationbehavior`, see below)
- **Collection Result Listing Sort** — let users sort the filtered results
- **Collection Filter Reset** — reset all active filters


## Filtering collections

Add filter/search portlets directly to a collection.
Selecting filter values reloads results asynchronously (no page refresh) via AJAX.

If your theme or view template needs customization for AJAX loading, adjust the `Content Selector` and/or `View Template` settings.
Make sure the selector exists on both the source collection template and the target page.

Filters can also target a remote collection — specify a `target collection` in the portlet/tile settings.
Without AJAX, selecting a filter option redirects to the collection.


## Mosaic integration

Install the extra:

```
pip install collective.collectionfilter[mosaic]
```

Add filter tiles via the Mosaic `Insert` menu and assign a collection.
Use a `Content Listing` tile to display results.

Multiple content listings and filters can coexist on the same page — use unique CSS classes in the listing tile settings and reference them in the filter tile's `Content Selector`.


## Geolocation support

Install the extra:

```
pip install collective.collectionfilter[geolocation]
```

This provides a LeafletJS map tile/portlet showing `IGeolocatable` collection items.
Enable `Narrow down results` to filter the collection and other tiles when the user pans or zooms the map.


## Customizing GroupByCriteria

`GroupByCriteria` is a global utility that defines which catalog indexes are available as filter criteria.

Each index entry has this structure:

```python
{
    'index': 'Subject',              # catalog index name
    'metadata': 'Subject',           # metadata column name
    'display_modifier': _,           # callable(value, index) -> display string
    'index_modifier': None,          # callable to transform search values
    'value_blacklist': [],           # values to exclude (list or callable)
    'sort_key_function': lambda it: it['title'].lower(),
}
```

To customize, register an `IGroupByModifier` adapter:

```python
from collective.collectionfilter.interfaces import IGroupByCriteria
from collective.collectionfilter.interfaces import IGroupByModifier
from zope.component import adapter
from zope.interface import implementer


@implementer(IGroupByModifier)
@adapter(IGroupByCriteria)
def groupby_modifier(groupby):
    groupby._groupby['Subject']['display_modifier'] = lambda x, idx: x.upper()
    groupby._groupby['my_custom_index'] = {
        'index': 'my_custom_index',
        'metadata': 'my_custom_metadata',
        'display_modifier': lambda val, idx: f'Custom: {val}',
    }
```

```xml
<configure xmlns="http://namespaces.zope.org/zope">
  <adapter factory=".mymodule.groupby_modifier" name="my_modifier" />
</configure>
```

The adapter is called by `GroupByCriteria.groupby`.
Modify the `_groupby` dict (not the `groupby` property, which triggers adapter lookup).


## Compatibility

- Version 6.x — Plone 6.2+
- Version 5.x — Plone 6.0+
- Version 4.x — Plone 5.2
- Version 3.x — Plone 5.0/5.1

If AJAX loading doesn't work with your theme, disable it in the registry or override via [diazo](https://docs.diazo.org/en/latest/index.html).


## Authors

- Johannes Raggam
- Peter Holzer

Based on [collective.portlet.collectionfilter](https://pypi.org/project/collective.portlet.collectionfilter/) and [collective.portlet.collectionbysubject](https://pypi.org/project/collective.portlet.collectionbysubject/).
