====================
cubicweb.calendar.js
====================
.. module:: cubicweb.calendar.js

This file contains Calendar utilities
 :organization: Logilab
 :copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr

.. class:: Calendar

  Calendar (graphical) widget

  public methods are :

  __init__ :
   :attr:`containerId`: the DOM node's ID where the calendar will be displayed
   :attr:`inputId`: which input needs to be updated when a date is selected
   :attr:`year`, :attr:`month`: year and month to be displayed
   :attr:`cssclass`: CSS class of the calendar widget (default is 'commandCal')

  show() / hide():
   show or hide the calendar widget

  toggle():
   show (resp. hide) the calendar if it's hidden (resp. displayed)

  displayNextMonth(): (resp. displayPreviousMonth())
   update the calendar to display next (resp. previous) month

.. function:: Calendar._uppercaseFirst(s)

   utility function (the only use for now is inside the calendar)

.. function:: Calendar._domForRows(rows)

   accepts the cells data and builds the corresponding TR nodes

* `rows`, a list of list of couples (daynum, cssprops)

.. function:: Calendar._headdisplay(row)

   builds the calendar headers

.. data:: Calendar.REGISTRY

    keep track of each calendar created

.. function:: toggleCalendar(containerId, inputId, year, month)

   popup / hide calendar associated to `containerId`

.. function:: toggleNextMonth(containerId)

   ask for next month to calendar displayed in `containerId`

.. function:: togglePreviousMonth(containerId)

   ask for previous month to calendar displayed in `containerId`

.. function:: dateSelected(cell, containerId)

   callback called when the user clicked on a cell in the popup calendar