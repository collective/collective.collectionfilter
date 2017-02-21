collective.collectionfilter
===========================

Faceted navigation filter for collection results.

This Plone addon allows you to filter collections results for additional catalog metadata.
For example, you can add a subject filter, but also a filter for authors or portal types.
This can also be used to build tag clouds.

The filter types can be extended (see: ``collective.collectionfilter.vocabularies``).

Besides the "Collection Filter" portlet/tile there is also a "Collection Search" portlet/tile for doing a fulltext search on the collection results.


Overloading GroupByCriteria
---------------------------

``collective.collectionfilter.vocabularies.GroupByCriteria`` is a singleton, registered as global utility and used to provide a list of possible indices, which grouped values will provide your filter criteria.

It uses a data structure like this::

    self._groupby = {
        _(it): {                   # Index name, possibly translated (TODO: probabyl shouldn't be translated)
            'index': it,           # Name of the index to use
            'metadata': it,        # Name of the metadata column to use
            'display_modifier': _  # Function to prepare the metadata column value for displaying
        }
        for it in metadata
    }

As you can see, the standard GroupByCriteriaVocabulary implementation implies, that the index name is the same as the metadata column name.
Also, we use the ``collective.collectionfilter`` message catalog as standard display_modifier (you can register translations under the ``collective.collectionfilter`` domain to translate index values).

If you need a special ``display_modifier``, or index or metadata columns do not have the same identifier, you can modify this data structure.
For that, retrieve the ``GroupByCriteria`` utility and pass a dictionary to ``groupby_modify``, which is used to update ``self._groupby``.
You have to wait for the global registry to finally set up, otherwise you'll get an ``ComponentLookupError``.

This is how.

Register an event subscriber listening to ``zope.processlifetime.IProcessStarting``, which is fired after the global registry is finished set up::

    <include package="collective.collectionfilter" />
    <subscriber
        for="zope.processlifetime.IProcessStarting"
        handler=".modify_groupby" />

Your ``modify_groupby`` looks like this::

    # -*- coding: utf-8 -*-
    from collective.collectionfilter.interfaces import IGroupByCriteria
    from zope.component import getUtility


    def modify_groupby(event):
        groupby = getUtility(IGroupByCriteria)
        groupby.groupby_modify = {'Subject': {'display_modifier': lambda x: x.upper()}}


Author
------

- Johannes Raggam
- Peter Holzer

This package is based on ``collective.portlet.collectionfilter`` and ``collective.portlet.collectionbysubject``.
