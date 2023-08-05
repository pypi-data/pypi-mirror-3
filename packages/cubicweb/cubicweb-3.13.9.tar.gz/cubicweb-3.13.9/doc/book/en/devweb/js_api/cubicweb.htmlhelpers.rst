=======================
cubicweb.htmlhelpers.js
=======================
.. module:: cubicweb.htmlhelpers.js

.. function:: baseuri()

returns the document's baseURI. (baseuri() uses document.baseURI if
available and inspects the <base> tag manually otherwise.)

.. function:: setProgressCursor()

set body's cursor to 'progress'

.. function:: resetCursor(result)

reset body's cursor to default (mouse cursor). The main
purpose of this function is to be used as a callback in the
deferreds' callbacks chain.

.. function:: asURL(props)

builds an url from an object (used as a dictionnary)

>>> asURL({'rql' : "RQL", 'x': [1, 2], 'itemvid' : "oneline"})
rql=RQL&vid=list&itemvid=oneline&x=1&x=2
>>> asURL({'rql' : "a&b", 'x': [1, 2], 'itemvid' : "oneline"})
rql=a%26b&x=1&x=2&itemvid=oneline

.. function:: firstSelected(selectNode)

return selected value of a combo box if any

.. function:: toggleVisibility(elemId)

toggle visibility of an element by its id

.. function:: popupLoginBox()

toggles visibility of login popup div

.. function getElementsMatching(tagName, properties, \/* optional \*\/ parent)

returns the list of elements in the document matching the tag name
and the properties provided

* `tagName`, the tag's name

* `properties`, a js Object used as a dict

Return an iterator (if a *real* array is needed, you can use the
                     list() function)

.. function:: setCheckboxesState(nameprefix, value, checked)

sets checked/unchecked status of checkboxes

.. function:: html2dom(source)

this function is a hack to build a dom node from html source