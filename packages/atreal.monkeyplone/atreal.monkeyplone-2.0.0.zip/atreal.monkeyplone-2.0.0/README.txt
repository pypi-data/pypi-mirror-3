.. contents::

Overview
========

atreal.monkeyplone display fullname in portlet review and change security for
cut/copy/paste/delete actions in Plone.


Compatibility
-------------

Plone 3 : Use the last version of branch 1.x.x.
Plone 4 : Use the last version of branch 2.x.x (this corresponds to the current version).

Note that the developement trunk only support Plone 4.

Description
============

Technically
-----------

* it changes the Permission on the tree methods : manage_cutObjects,
  manage_delObjects and manage_pasteObjects of BaseFolderMixin from
  Products.Archetypes.BaseFolder.

* it patches the method _verifyObjectPaste from Products.CMFCore.PortalFolder
  who check the delete permission on parent object.
  
* it applies on actions this modifications.


Functionnally
-------------

 When a user "can add" on a folder, now he can cut and delete his own creation.


Note
====

Use with precaution;)


Authors
=======

|atreal|_

* `atReal Team`_

  - Jean-Nicolas Bes [drjnut]
  - Florent Michon [f10w]

.. |atreal| image:: http://downloads.atreal.net/logos/atreal-logo-48-white-bg.png
.. _atreal: http://www.atreal.net
.. _atReal Team: mailto:contact@atreal.net


Contributors
============

* `atReal Team`_

  - Romain BEYLERIAN [rbeylerian]

.. _atReal Team: mailto:contact@atreal.fr
