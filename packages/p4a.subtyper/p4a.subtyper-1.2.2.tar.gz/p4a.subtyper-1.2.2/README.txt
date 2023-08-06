p4a.subtyper
============

p4a.subtyper is a subtyping framework for Plone.  In this context, subtyping
means to provide additional specific types onto existing content types.  An
example to standard Plone would be to have only one File content type (and no
Image content type).  The Image content type would then become a sub-type
of the File content type.

It also exposes the possible sub-types for a given object in the content menu
with a sub-types dropdown menu.

See ``browser/browser.txt`` for example usage.

Requirements
------------

  * Plone 2.5, Plone 3.x or Plone 4.x

Credits
-------

Originally created by Rocky Burt (rocky AT serverzen DOT com --
http://www.serverzen.com) on behalf of Jazkarta Inc (http://www.jazkarta.com).
