===========
cubicweb.js
===========
.. module:: cubicweb.js

.. function:: jqNode(node)

safe version of jQuery('#nodeid') because we use ':' in nodeids
which messes with jQuery selection mechanism

.. function:: toISOTimestamp(date)

.. function:: nodeWalkDepthFirst(node, visitor)

depth-first implementation of the nodeWalk function found
in `MochiKit.Base <http://mochikit.com/doc/html/MochiKit/Base.html#fn-nodewalk>`_

.. function:: formContents(elem \/* = document.body *\/)

this implementation comes from MochiKit

.. function:: sliceList(lst, start, stop, step)

returns a subslice of `lst` using `start`/`stop`/`step`
start, stop might be negative

>>> sliceList(['a', 'b', 'c', 'd', 'e', 'f'], 2)
['c', 'd', 'e', 'f']
>>> sliceList(['a', 'b', 'c', 'd', 'e', 'f'], 2, -2)
['c', 'd']
>>> sliceList(['a', 'b', 'c', 'd', 'e', 'f'], -3)
['d', 'e', 'f']

returns the last element of an array-like object or undefined if empty

.. function:: extend(array1, array2)

equivalent of python ``+=`` statement on lists (array1 += array2)

.. function:: difference(lst1, lst2)

returns a list containing all elements in `lst1` that are not
in `lst2`.

.. function:: domid(string)

return a valid DOM id from a string (should also be usable in jQuery
search expression...). This is the javascript implementation of
:func:`cubicweb.uilib.domid`.

.. function:: strFuncCall(fname, *args)

return a string suitable to call the `fname` javascript function with the
given arguments (which should be correctly typed).. This is providing
javascript implementation equivalent to :func:`cubicweb.uilib.js`.

DOM factories ***********************************************************