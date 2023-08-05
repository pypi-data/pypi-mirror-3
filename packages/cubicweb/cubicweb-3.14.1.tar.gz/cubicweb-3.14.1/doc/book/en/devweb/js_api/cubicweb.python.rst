==================
cubicweb.python.js
==================
.. module:: cubicweb.python.js

This file contains extensions for standard javascript types

.. function:: Date.prototype.nextMonth()

returns the first day of the next month

.. function:: Date.prototype.getRealDay()

returns the day of week, 0 being monday, 6 being sunday

.. function:: _parseDate(datestring, format)

_parseData does the actual parsing job needed by `strptime`

.. function:: strptime(datestring, format)

basic implementation of strptime. The only recognized formats
defined in _DATE_FORMAT_REGEXES (i.e. %Y, %d, %m, %H, %M)

.. function:: String.prototype.startswith(prefix)

python-like startsWith method for js strings
>>>

.. function:: String.prototype.endswith(suffix)

python-like endsWith method for js strings

.. function:: String.prototype.strip()

python-like strip method for js strings

.. function:: String.prototype.rstrip()

python-like rstrip method for js strings

.. function:: makeUnboundMethod(meth)

transforms a function into an unbound method

.. function:: _isAttrSkipped(attrname)

simple internal function that tells if the attribute should
be copied from baseclasses or not

.. function:: makeConstructor(userctor)

internal function used to build the class constructor

.. function:: defclass(name, bases, classdict)

this is a js class factory. objects returned by this function behave
more or less like a python class. The `class` function prototype is
inspired by the python `type` builtin

.. Note::

   * methods are _STATICALLY_ attached when the class it created
   * multiple inheritance was never tested, which means it doesn't work ;-)