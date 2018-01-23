Changelog
=========

1.0 (unreleased)
----------------

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
