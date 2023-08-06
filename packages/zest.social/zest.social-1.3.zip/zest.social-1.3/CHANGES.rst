Changelog
=========

1.3 (2012-09-12)
----------------

- Moved to github.
  [maurits]


1.2 (2010-10-19)
----------------

- Added MANIFEST.in file so the released package will contain ``.mo``
  files (at least when using ``zest.releaser`` in combination with
  ``zest.pocompile``).
  [maurits]

- When context.show_social_viewlet does not work, try 
  context.getField('show_social_viewlet').get(context)
  as somehow the first only works when you have called getField once.
  Tested with archetypes.schemaextender 1.6 and 2.0.3.
  [maurits]

- Added config.py to ease overriding the 
  default value for the show_social_viewlet field (False)
  and the fallback value for when the field does not exist for the
  current object (False).
  [maurits]


1.1 (2010-10-18)
----------------

- Explicitly load the zcml of the archetypes.schemaextender package so
  you do not need to add this yourself to your buildout config on
  Plone 3.2 or earlier.
  [maurits]


1.0 (2010-10-18)
----------------

- Initial release.  [maurits]
