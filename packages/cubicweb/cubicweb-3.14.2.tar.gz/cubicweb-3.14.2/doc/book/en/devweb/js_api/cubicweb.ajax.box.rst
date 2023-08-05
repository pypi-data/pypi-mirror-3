====================
cubicweb.ajax.box.js
====================
.. module:: cubicweb.ajax.box.js

Functions for ajax boxes.

 :organization: Logilab
 :copyright: 2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr

.. function:: ajaxBoxShowSelector(boxid, eid, unrelfname,
                                 addfname, msg,
                                 oklabel, cancellabel,
                                 separator=None)

Display an ajax selector within a box of regid `boxid`, for entity with eid
`eid`.

Other parameters are:

* `addfname`, name of the json controller method to call to add a relation

* `msg`, message to display to the user when a relation has been added

* `oklabel`/`cancellabel`, OK/cancel buttons label

* `separator`, items separator if the field is multi-valued (will be
  considered mono-valued when not specified)