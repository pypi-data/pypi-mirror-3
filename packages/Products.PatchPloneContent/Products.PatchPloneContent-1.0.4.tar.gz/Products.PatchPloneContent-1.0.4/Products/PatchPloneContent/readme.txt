PatchPloneContent is a collection of utilities, used to add or alter
how standard Plone content types work using the monkeypatch technique.

Variables of interest in this module are content_types, a tuple
collection of the class definitions of standard content types.

The functions of interest are content_classes_add_fields, which
accepts a sequence of content classes as the first argument, and a
sequence of fields to add as the second argument.  As well as
add_validator, which inserts validators into fields.

Should work with Plone 3 and 4, maybe 2 as well.

Note that archetypes.schemaextender is a perhaps bit more difficult
product to use but more powerful.

Written by Morten W. Petersen, info@nidelven-it.no
