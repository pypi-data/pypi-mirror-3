===================
cubicweb.widgets.js
===================
.. module:: cubicweb.widgets.js

Functions dedicated to widgets.

 :organization: Logilab
 :copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr

.. function:: buildWidget(wdgnode)

this function takes a DOM node defining a widget and
instantiates / builds the appropriate widget class

.. function:: buildWidgets(root)

This function is called on load and is in charge to build
JS widgets according to DOM nodes found in the page

`hiddenInputHandlers` defines all methods specific to handle the
hidden input created along the standard text input.
An hiddenInput is necessary when displayed suggestions are
different from actual values to submit.
Imagine an autocompletion widget to choose among a list of CWusers.
Suggestions would be the list of logins, but actual values would
be the corresponding eids.
To handle such cases, suggestions list should be a list of JS objects
with two `label` and `value` properties.

.. class:: Widgets.SuggestForm

suggestform displays a suggest field and associated validate / cancel buttons
constructor's argumemts are the same that BaseSuggestField widget

.. function:: toggleTree(event)

called when the use clicks on a tree node
 - if the node has a `cubicweb:loadurl` attribute, replace the content of the node
   by the url's content.
 - else, there's nothing to do, let the jquery plugin handle it.

.. class:: Widgets.TimelineWidget

widget based on SIMILE's timeline widget
http://code.google.com/p/simile-widgets/

Beware not to mess with SIMILE's Timeline JS namepsace !

.. function:: insertText(text, areaId)

inspects textarea with id `areaId` and replaces the current selected text
with `text`. Cursor is then set at the end of the inserted text.