Changelog
=========

3.0 (2019-03-25)
----------------

Breaking changes:

- Remove support for Plone < 5.1.
  [petschki]

New features:

- Python 3 compatibility.
  [petschki]

- Test setup
  [petschki]

Bug fixes:

- fix bug in @@render-portlet for Python 3.
  NOTE on Python 3: this required plone.app.portlets >= 4.4.2
  [petschki]


2.1 (2019-03-22)
----------------

New features:

- Python 3 compatibility.
  [agitator]

Bug fixes:

- Do not render an empty ``filterClassName``.
  [thet]

- patCollectionFilter is not in settings, it’s in view.
  [agitator]

- Fix styles for long/multiline filter terms
  [agitator]


2.0.1 (2018-12-13)
------------------

- Fix upgrade steps and reapply profile to fix bundle registration
  Remove conditional reinitialization - caused problems with other patterns
  [agitator]


2.0 (2018-12-08)
----------------

Breaking changes:

- Remove the ``cache_time`` setting and replace it with ``cache_enabled``.

- collectionsearch.pt: changed view attribute ``header_title`` to ``title``.

- Depend on plone.app.contenttypes.
  All target collections must provide ``plone.app.contenttypes.behaviors.collection.ICollection`` interface.
  The ``result`` method will be callend on this behavior adapter.

- There is a implicit dependency to Font Awesome for the filter tile edit links.
  That has to be revisited to make it work out of the box.

- Modernized markup for easier styling

New:

- Optimize the cache key by including the current language, user roles instead of id and the database counter.

- Remove the view_name part when populating the browser history with filter changes.
  The view_name part is for loading specific AJAX tiles, but should probably not be displayed.

- Add filter and search tiles.

- Add a ``sort_key_function`` key to the IQueryModifier dict to allow for a different sort key function when sorting the values.

- Add a ``index_modifier`` key to the IQueryModifier indexes dict to allow transforming of index search values.
  For ``KeywordIndex`` indices the index_modifier is automatically set to encode the value to utf-8.

- Add a ``value_blacklist`` key to the IQueryModifier indexes dict to allow blacklisting of individual index values.

- Add ``view_name`` configuration parameter to call a special result listing view.
  This can be used to call a tile instead to call the whole context view.

- Add ``content_selector`` configuration parameter to choose a DOM node from the source to inject into the target.

- Ensure early exit on the content filter traverse handler if it is not needed to run.

- Make backwards compatible with Plone 5.0
  [nngu6036, instification]

Bug fixes:

- When reloading the collection in JavaScript, use the content selector's parent as base to trigger events on.
  The content selector itself is replaced and events cannot be catched.

- Register the bundle compile files as ``collectionfilter-bundle-compiled.js`` and ``collectionfilter-bundle-compiled.css``, so that using ``plone-compile-resources`` results in the same files.
  See: https://github.com/plone/Products.CMFPlone/issues/2437

- Sort the filter value list for filter title instead filter value.

- fix collectionsearch portlet
  [petschki]

- when providing a custom `IGroupByCriteria` adapter, fallback to title sorted values if no sort_key_function is given.
  [petschki]


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
