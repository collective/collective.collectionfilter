collective.portlet.collectionfilter
===================================

Introduction
------------

This portlet makes it possible to present collections grouped by different criteria including:

* by Author
* by Keyword
* by Type
* by Location (may require some tweaking)


Usage
-----
Click "manage portlets" and add a new "Collection by subject".

Settings include:

Portlet header - the title of the portlet
Target collection - the collection that the portlet will use
Group by - the subject that you would like to group the items by
Cache duration - the lenghth of time the results should be cached

The output looks similar to this::

      by Keyword

        food (4)
        green (2)
        drink (4)
        well (2)
        sleep (1)


Authors
-------

Refactoring into collective.portlet.collectionfilter by Johannes Raggam.

Original implementation of collective.portlet.collectionbysubject by Rok
Garbas. Concept by David Bain (alteroo.com).
