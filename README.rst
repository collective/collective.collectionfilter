collective.collectionfilter
===========================

Faceted navigation filter for collection results.

This Plone 5 addon allows you to filter collections results for additional catalog metadata.
For example, you can add a subject filter, but also a filter for authors or portal types.
This can also be used to build tag clouds.

The filter types can be extended (see: ``collective.collectionfilter.vocabularies``).

There are four portlets/tiles available for filtering:

``Collection Filter``
    a list with values (select, radio, checkbox, link) you can filter on
``Collection Search``
    a SearchableText input field to do a fulltextsearch on the collection results
``Collection Maps``
    a LeafletJS map which shows and filters ``IGeolocatable`` items on it
    (this feature is available if ``collective.geolocationbehavior`` is installed and the behavior
    is activated on a contenttype. See installation notes below)
``Section Filter``
    a list of site sections (folders) you can filter on


Filter Results with portlets
----------------------------

Add as many of the filter portlets above to any context you want (most likely the source collection)
and assign a collection with results to it.

When you select values from the filter the results are loaded asynchronously inside the container
with the selector defined in the field ``Content Selector``. Make sure the selector exists on the
source collection template and on the target page which shows the filtered results.


Mosaic Integration
------------------

The tiles can be added within the Mosaic editor multiple times. Just select them in the ``Insert`` menu
and assign a collection to it. To show the results of the collection simply add a
``Existing Content`` tile which links to the same collection your filter tiles are assigned with.

TODO: right now the collection needs a default_view template, which wraps the result list with a unique selector
inside the ``#content-core`` container. so the collectionfilter can load the filtered result correctly from
the collection into the container inside the existing content tile.


Geolocation filter support
--------------------------

If ``collective.geolocationbehavior`` is installed, this package provides a LeafletJS Maps tile/portlet
which shows each item of a collection result if the ``IGeolocatable`` information is available.
In addition you can activate the ``Narrow down results`` checkbox to narrow down the collection result and
other available filter tiles/portlets if the user moves or zooms the map.

We provide a package extra to install all required dependencies with their according versions.
Simply do this somewhere in your buildout::

    [buildout]
    ...
    eggs +=
        collective.collectionfilter[geolocation]
    ...


Overloading GroupByCriteria
---------------------------

``collective.collectionfilter.vocabularies.GroupByCriteria`` is a singleton, registered as global utility and used to provide a list of possible indices, which grouped values will provide your filter criteria.

It uses a data structure like this::

    self._groupby = {
        it: {                   # Index name
            'index': it,             # Name of the index to use
            'metadata': it,          # Name of the metadata column to use
            'display_modifier': _ ,  # Function to prepare the metadata column value for displaying
            'index_modifier': None,  # Function to transform the index search value.
            'value_blacklist': [],   # Blacklist of index values, which should not included in the filter selection. Can be a callable.
            'sort_key_function': lambda it: it['title'].lower(),  # sort key function. defaults to a lower-cased title
        }
        for it in metadata
    }

As you can see, the standard GroupByCriteriaVocabulary implementation implies, that the index name is the same as the metadata column name.
Also, we use the ``collective.collectionfilter`` message catalog as standard display_modifier (you can register translations under the ``collective.collectionfilter`` domain to translate index values).

If you need a special ``display_modifier``, or index or metadata columns do not have the same identifier, you can modify this data structure.
For that, register an adapter for ``IGroupByModifier``, which adapts to the GroupByCriteria utility.
Within this adapter, you can modify the already populated ``_groupby`` attribute (do not use the ``groupby``, which is a property method and at this point hasn't finished).

This is how.

Write an adapter::

    # -*- coding: utf-8 -*-
    from collective.collectionfilter.interfaces import IGroupByCriteria
    from collective.collectionfilter.interfaces import IGroupByModifier
    from zope.component import adapter
    from zope.interface import implementer


    sort_map = {
        'VALUE1': 3,
        'VALUE2': 1,
        'VALUE3': 2,
    }


    def subjectsort(it):
        # Sorts the value after a fixed sort map
        val = it['title']
        return sort_map.get(val, 0)


    @implementer(IGroupByModifier)
    @adapter(IGroupByCriteria)
    def groupby_modifier(groupby):
        groupby._groupby['Subject']['display_modifier'] = lambda x: x.upper()
        groupby._groupby['Subject']['sort_key_function'] = subjectsort
        groupby._groupby['my_new_index'] = {
            'index': 'my_new_index',
            'metadata': 'my_new_index_metadata_colum',
            'display_modifier': lambda it: u'this is awesome: {0}'.format(it)
        }

Register the adapter::

    <configure xmlns="http://namespaces.zope.org/zope">
      <adapter factory=".collectionfilter.groupby_modifier" name="modifier_1" />
    </configure>

Done.

Your adapter is called by ``collective.collectionfilter.vocabularies.GroupByCriteria.groupby``.

Compatibility
-------------

This package is compatible with Plone 5 and above. Note that in 5.0 some functionality is reduced such as AJAX loading of search results.
If your theme doesn't work well with AJAX loading this can be overridden in the registery or via diazo.

Author
------

- Johannes Raggam
- Peter Holzer

This package is based on ``collective.portlet.collectionfilter`` and ``collective.portlet.collectionbysubject``.
