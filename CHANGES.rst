Changelog
=========

1.4.1 (2016-02-04)
------------------

- Fix AJAX loading of collectionfilter result to use the #content node instead of whole document.
  [thet]


1.4 (2015-12-17)
----------------

- Set the 'selected' class on clicked collectionfilter link via JavaScript.
  [thet]


1.3 (2015-12-15)
----------------

- Plone 5 compatibility.
  [agitator]

- Ajaxification with mockup, if available.
  [agitator]


1.2 (2015-12-14)
----------------

- Make cache time configurable and set it to 60 seconds instead of an hour.
  0 is no caching.
  Remove profiling code.
  [thet]


1.1.3 (2015-09-25)
------------------

- Fix brown bag release.
  [thet]


1.1.2 (2015-09-25)
------------------

- In the collection filter portlet, don't count empty values. These cannot be
  searched via the catalog. Use an empty marker instead (for an example on the
  ``Subject`` index, see the indexer module).
  [thet]


1.1.1 (2015-09-25)
------------------

- Fix error with rendering the portlet and having an empty subject.
  [thet]


1.1 (2015-09-25)
----------------

- Add a subject indexer, which adds EMPTY_MARKER to the index, where no subject
  is set. Make sure, the EMPTY_MARKER is translated in the portlet.
  [thet]


1.0 (2015-07-15)
----------------

- Fork from collective.portlet.collectionbysubject and complete refactoring.
  [thet]
