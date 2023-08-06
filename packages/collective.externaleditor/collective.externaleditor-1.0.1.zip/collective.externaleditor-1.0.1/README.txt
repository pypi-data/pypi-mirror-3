.. contents::

Overview
========

A specific Plone layer for Products.ExternalEditor


Description
===========

This package add a Control Panel to enable or disable external editor
(ext_editor property in Plone seems to be unused) and to choose on which
content types action will be available.

Technically this package add a skin layer to override external_edit.py and
externalEditorEnabled.py python scripts from Plone to make them call
views. These views respect the same behavior as today in Plone but add
security checks (now you need "Modify Portal Content" to call external_edit)
and add the support for content types you choose in the configlet.

Permissions 'WebDAV Unlock items' and 'WebDAV Lock items' are given to the
'Editor' role. IMPORTANT : previous settings for these permissions will be
erased.


Important
=========

collective.externaleditor is only working with Products.ExternalEditor >= 1.1.0
so you need to pin the version of Products.ExternalEditor in your buildout. ::
    
    [versions]
    Products.ExternalEditor = 1.1.0


Todo
====

* More test cover
* Add in configlet the possibility to activate or unactivate external editor
  property for all users
* Add in configlet the possibility to activate external editor for the new users


Authors
=======

|atreal|_

* `atReal Team`_

  - Thierry Benita [tbenita]
  - Matthias Broquet [tiazma]
  - Florent Michon [f10w]

.. |atreal| image:: http://downloads.atreal.net/logos/atreal-logo-48-white-bg.png
.. _atreal: http://www.atreal.net
.. _atReal Team: mailto:contact@atreal.net


Credits
=======

* Sponsorised by LESAFFRE - <http://www.lesaffre.com/>
