===================
cubicweb.edition.js
===================
.. module:: cubicweb.edition.js

Functions dedicated to edition.

 :organization: Logilab
 :copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr

.. function:: setPropValueWidget(varname, tabindex)

called on CWProperty key selection:
- get the selected value
- get a widget according to the key by a sync query to the server
- fill associated div with the returned html

* `varname`, the name of the variable as used in the original creation form
* `tabindex`, the tabindex that should be set on the widget

.. function:: reorderTabindex(start, formid)

this function is called when an AJAX form was generated to
make sure tabindex remains consistent

.. function:: _showMatchingSelect(eid, divNode)

* `divNode`, a jQuery selection

.. function:: buildPendingInsertHandle(elementId, element_name, selectNodeId, eid)

this function builds a Handle to cancel pending insertion

.. function:: buildPendingDeleteHandle(elementId, eid)

this function builds a Handle to cancel pending insertion

.. function:: addPendingDelete(nodeId, eid)

* `nodeId`, eid_from:r_type:eid_to

.. function:: cancelPendingDelete(nodeId, eid)

* `nodeId`, eid_from:r_type:eid_to

.. function:: togglePendingDelete(nodeId, eid)

* `nodeId`, eid_from:r_type:eid_to

.. function:: addInlineCreationForm(peid, petype, ttype, rtype, role, i18nctx, insertBefore)

makes an AJAX request to get an inline-creation view's content
* `peid`, the parent entity eid

* `petype`, the parent entity type

* `ttype`, the target (inlined) entity type

* `rtype`, the relation type between both entities

.. function:: removeInlineForm(peid, rtype, role, eid, showaddnewlink)

removes the part of the form used to edit an inlined entity

.. function:: removeInlinedEntity(peid, rtype, eid)

alternatively adds or removes the hidden input that make the
edition of the relation `rtype` possible between `peid` and `eid`
* `peid`, the parent entity eid

* `rtype`, the relation type between both entities

* `eid`, the inlined entity eid

.. function:: unfreezeFormButtons(formid)

unfreeze form buttons when the validation process is over

.. function:: freezeFormButtons(formid)

disable form buttons while the validation is being done

.. function:: postForm(bname, bvalue, formid)

used by additional submit buttons to remember which button was clicked

.. function:: setFormsTarget(node)

called on load to set target and iframeso object.

.. note::

   this is a hack to make the XHTML compliant.

.. note::

  `object` nodes might be a potential replacement for iframes

.. note::

   there is a XHTML module allowing iframe elements but there
   is still the problem of the form's `target` attribute

.. function:: validateForm(formid, action, onsuccess, onfailure)

called on traditionnal form submission : the idea is to try
to post the form. If the post is successful, `validateForm` redirects
to the appropriate URL. Otherwise, the validation errors are displayed
around the corresponding input fields.