Changelog
=========

2.0 (unreleased)
----------------

Breaking changes:

- Portlet classes ``portletCollectionFilter`` and ``portletCollectionSearch`` are renaned to ``collectionSearch`` and ``collectionFilter``.

- Depend on Products.CMFPlone >= 5.1 for using ``get_top_request``.
- collectionsearch.pt: changed ``header_title`` to ``title``.

- Depend on plone.app.contenttypes.
  All target collections must provide ``plone.app.contenttypes.behaviors.collection.ICollection`` interface.
  The ``result`` method will be callend on this behavior adapter.

- There is a implicit dependency to Font Awesome for the filter tile edit links.
  That has to be revisited to make it work out of the box.

New:

- Remove the view_name part when populating the browser history with filter changes.
  The view_name part is for loading specific AJAX tiles, but should probably not be displayed.

- Add filter and search tiles.

- Add a ``index_modifier`` key to the IQueryModifier indexes dict to allow transforming of index search values.
  For ``KeywordIndex`` indices the index_modifier is automatically set to encode the value to utf-8.

- Add a ``value_blacklist`` key to the IQueryModifier indexes dict to allow blacklisting of individual index values.

- Add ``view_name`` configuration parameter to call a special result listing view.
  This can be used to call a tile instead to call the whole context view.

- Add ``content_selector`` configuration parameter to choose a DOM node from the source to inject into the target.

- Ensure early exit on the content filter traverse handler if it is not needed to run.

Bug fixes:

- Sort the filter value list for filter title instead filter value.


1.0.1 (2018-02-09)
------------------

- Fix target collection selection via catalog vocabular and RelatedItemsFieldWidget.
  [agitator]


1.0 (2018-01-27)
----------------

- Implement AJAX search for the collection search portlet.
  [thet]

- Update the history / location bar URL with the current filter URL.
  [thet]

- Fix error where ``closest`` DOM method isn't supported on IE.
  Fixes #6.
  [agitator]

- Register bundle to depend on ``*`` to avoid weird Select2 initialization error.
  [thet]

- Add ``input_type`` option to be able to better select the type of input.
  Add ``input_type`` support for dropdowns.
  Remove ``as_input`` attribute and provide upgrade step for it.
  [thet]

- Initial release from collective.portlet.collectionfilter.
  [thet]
