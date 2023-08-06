Introduction
============

Description
-------------

- This product is order change for Plone container.
- control panel setting on default when creating new folder.


Requirement
-------------

- Plone

  - Plone 4.0 (tested by 4.0 on MacOS 10.6)
  - Plone 3.x (tested by 3.3.4 on MacOS 10.6)


Note for Plone 3.2.x
-----------------------
You need to add on buildout.cfg

buildout.cfg

::

   [buildout]
   eggs =
      ...
      c2.patch.contentslist

   zcml =
      ...
      c2.patch.contentslist
      c2.patch.contentslist-overrides

   [versions]
   archetypes.schemaextender = 2.0.3
