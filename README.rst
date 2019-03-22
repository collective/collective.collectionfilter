collective.collectionfilter
===========================

Faceted navigation filter for collection results.

This Plone 5 addon allows you to filter collections results for additional catalog metadata.
For example, you can add a subject filter, but also a filter for authors or portal types.
This can also be used to build tag clouds.

The filter types can be extended (see: ``collective.collectionfilter.vocabularies``).

Besides the "Collection Filter" portlet/tile there is also a "Collection Search" portlet/tile for doing a fulltext search on the collection results.


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

This package is compatible with Plone 5.1 and above.

Author
------

- Johannes Raggam
- Peter Holzer

This package is based on ``collective.portlet.collectionfilter`` and ``collective.portlet.collectionbysubject``.
