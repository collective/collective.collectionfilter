collective.collectionfilter
===========================

Faceted navigation filter for collection results.

This Plone addon allows you to filter collections results for additional catalog metadata.
For example, you can add a subject filter, but also a filter for authors or portal types.
This can also be used to build tag clouds.

The filter types can be extended (see: ``collective.collectionfilter.vocabularies``).

Besides the "Collection Filter" portlet/tile there is also a "Collection Search" portlet/tile for doing a fulltext search on the collection results.

This package is based on ``collective.portlet.collectionfilter`` and ``collective.portlet.collectionbysubject``.



Settings
--------

``Filter Type``:
    Select if single or multiple criterias can be selected and if all (and) or any (or) of the selected criterias must be met.
    Some index types like ``FieldIndex`` (e.g. Type index) only support the any (or) criteria when set to multiple criterias and ignore, if all (and) is set.
