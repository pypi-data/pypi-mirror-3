============================
Using the flufl.enum library
============================

The ``flufl.enum`` package provides yet another enumeration data type for
Python.  While this is similar intent to the reject `PEP 354`_, this package
defines an alternative syntax and semantics.

An enumeration is a set of symbolic names bound to unique, constant integer
values.  Within an enumeration, the values can be compared by identity, and
the enumeration itself can be iterated over.  Enumeration items can be
converted to and from their integer equivalents, supporting use cases such as
storing enumeration values in a database.


Motivation
==========

[Lifted from PEP 354]

The properties of an enumeration are useful for defining an immutable, related
set of constant values that have a defined sequence but no inherent semantic
meaning.  Classic examples are days of the week (Sunday through Saturday) and
school assessment grades ('A' through 'D', and 'F').  Other examples include
error status values and states within a defined process.

It is possible to simply define a sequence of values of some other basic type,
such as ``int`` or ``str``, to represent discrete arbitrary values.  However,
an enumeration ensures that such values are distinct from any others, and that
operations without meaning ("Wednesday times two") are not defined for these
values.


Creating an Enum
================

Enumerations are created using the class syntax, which makes them easy to read
and write.  Every enumeration value must have a unique integer value and the
only restriction on their names is that they must be valid Python identifiers.
To define an enumeration, derive from the Enum class and add attributes with
assignment to their integer values.

    >>> from flufl.enum import Enum
    >>> class Colors(Enum):
    ...     red = 1
    ...     green = 2
    ...     blue = 3

Enumeration values are compared by identity.

    >>> Colors.red is Colors.red
    True
    >>> Colors.blue is Colors.blue
    True
    >>> Colors.red is not Colors.blue
    True
    >>> Colors.blue is Colors.red
    False

Enumeration values have nice, human readable string representations...

    >>> print(Colors.red)
    Colors.red

...while their repr has more information.

    >>> print(repr(Colors.red))
    <EnumValue: Colors.red [int=1]>

The enumeration value names are available through the class members.

    >>> for member in Colors.__members__:
    ...     print(member)
    red
    green
    blue

Let's say you wanted to encode an enumeration value in a database.  You might
want to get the enumeration class object from an enumeration value.

    >>> cls = Colors.red.enum
    >>> print(cls.__name__)
    Colors

Enums also have a property that contains just their item name.

    >>> print(Colors.red.name)
    red
    >>> print(Colors.green.name)
    green
    >>> print(Colors.blue.name)
    blue

The str and repr of the enumeration class also provides useful information.

    >>> print(Colors)
    <Colors {red: 1, green: 2, blue: 3}>
    >>> print(repr(Colors))
    <Colors {red: 1, green: 2, blue: 3}>

You can extend previously defined Enums by subclassing.

    >>> class MoreColors(Colors):
    ...     pink = 4
    ...     cyan = 5

When extended in this way, the base enumeration's values are identical to the
same named values in the derived class.

    >>> Colors.red is MoreColors.red
    True
    >>> Colors.blue is MoreColors.blue
    True

However, these are not doing comparisons against the integer equivalent
values, because if you define an enumeration with similar item names and
integer values, they will not be identical.

    >>> class OtherColors(Enum):
    ...     red = 1
    ...     blue = 2
    ...     yellow = 3
    >>> Colors.red is OtherColors.red
    False
    >>> Colors.blue is not OtherColors.blue
    True

These enumeration values are not equal, nor do they hash equally.

    >>> Colors.red == OtherColors.red
    False
    >>> len(set((Colors.red, OtherColors.red)))
    2

Ordered comparisons between enumeration values are *not* supported.  Enums are
not integers!

    >>> Colors.red < Colors.blue
    Traceback (most recent call last):
    ...
    NotImplementedError
    >>> Colors.red <= Colors.blue
    Traceback (most recent call last):
    ...
    NotImplementedError
    >>> Colors.blue > Colors.green
    Traceback (most recent call last):
    ...
    NotImplementedError
    >>> Colors.blue >= Colors.green
    Traceback (most recent call last):
    ...
    NotImplementedError

Equality comparisons are defined though.

    >>> Colors.blue == Colors.blue
    True
    >>> Colors.green != Colors.blue
    True

Enumeration values do not support ordered comparisons.

    >>> Colors.red < Colors.blue
    Traceback (most recent call last):
    ...
    NotImplementedError
    >>> Colors.red < 3
    Traceback (most recent call last):
    ...
    NotImplementedError
    >>> Colors.red <= 3
    Traceback (most recent call last):
    ...
    NotImplementedError
    >>> Colors.blue > 2
    Traceback (most recent call last):
    ...
    NotImplementedError
    >>> Colors.blue >= 2
    Traceback (most recent call last):
    ...
    NotImplementedError

While equality comparisons are allowed, comparisons against non-enumeration
values will always compare not equal.

    >>> Colors.green == 2
    False
    >>> Colors.blue == 3
    False
    >>> Colors.green != 3
    True
    >>> Colors.green == 'green'
    False

If you really want the integer equivalent values, you can convert enumeration
values explicitly using the ``int()`` built-in.  This is quite convenient for
storing enums in a database for example.

    >>> int(Colors.red)
    1
    >>> int(Colors.green)
    2
    >>> int(Colors.blue)
    3

You can also convert back to the enumeration value by calling the Enum class,
passing in the integer value for the item you want.

    >>> Colors(1)
    <EnumValue: Colors.red [int=1]>
    >>> Colors(2)
    <EnumValue: Colors.green [int=2]>
    >>> Colors(3)
    <EnumValue: Colors.blue [int=3]>
    >>> Colors(1) is Colors.red
    True

The Enum class also accepts the string name of the enumeration value.

    >>> Colors('red')
    <EnumValue: Colors.red [int=1]>
    >>> Colors('blue') is Colors.blue
    True

You get exceptions though, if you try to use invalid arguments.

    >>> Colors('magenta')
    Traceback (most recent call last):
    ...
    ValueError: magenta
    >>> Colors(99)
    Traceback (most recent call last):
    ...
    ValueError: 99

The Enum base class also supports getitem syntax, exactly equivalent to the
class's call semantics.

    >>> Colors[1]
    <EnumValue: Colors.red [int=1]>
    >>> Colors[2]
    <EnumValue: Colors.green [int=2]>
    >>> Colors[3]
    <EnumValue: Colors.blue [int=3]>
    >>> Colors[1] is Colors.red
    True
    >>> Colors['red']
    <EnumValue: Colors.red [int=1]>
    >>> Colors['blue'] is Colors.blue
    True
    >>> Colors['magenta']
    Traceback (most recent call last):
    ...
    ValueError: magenta
    >>> Colors[99]
    Traceback (most recent call last):
    ...
    ValueError: 99

The integer equivalent values serve another purpose.  You may not define two
enumeration values with the same integer value.

    >>> class Bad(Enum):
    ...     cartman = 1
    ...     stan = 2
    ...     kyle = 3
    ...     kenny = 3 # Oops!
    ...     butters = 4
    Traceback (most recent call last):
    ...
    TypeError: Multiple enum values: 3

You also may not duplicate values in derived enumerations.

    >>> class BadColors(Colors):
    ...     yellow = 4
    ...     chartreuse = 2 # Oops!
    Traceback (most recent call last):
    ...
    TypeError: Multiple enum values: 2

The Enum class support iteration.  Enumeration values are returned in the
sorted order of their integer equivalent values.

    >>> [v.name for v in MoreColors]
    ['red', 'green', 'blue', 'pink', 'cyan']
    >>> [int(v) for v in MoreColors]
    [1, 2, 3, 4, 5]

Enumeration values are hashable, so they can be used in dictionaries and sets.

    >>> apples = {}
    >>> apples[Colors.red] = 'red delicious'
    >>> apples[Colors.green] = 'granny smith'
    >>> for color in sorted(apples, key=int):
    ...     print(color.name, '->', apples[color])
    red -> red delicious
    green -> granny smith


Pickling
========

Enumerations created with the class syntax can also be pickled and unpickled:

    >>> from flufl.enum.tests.fruit import Fruit
    >>> from pickle import dumps, loads
    >>> Fruit.tomato is loads(dumps(Fruit.tomato))
    True


Alternative API
===============

You can also create enumerations using the convenience function `make()`,
which takes an iterable object or dictionary to provide the item names and
values.  `make()` is a static method.

.. note::

   The `make_enum()` function from earlier releases is deprecated.  Use
   `make()` instead.

The first argument to `make()` is the name of the enumeration, and it returns
the so-named `Enum` subclass.  The second argument is a `source` which can be
either an iterable or a dictionary.  In the most basic usage, `source` returns
a sequence of strings which name the enumeration items.  In this case, the
values are automatically assigned starting from 1::

    >>> from flufl.enum import make
    >>> make('Animals', ('ant', 'bee', 'cat', 'dog'))
    <Animals {ant: 1, bee: 2, cat: 3, dog: 4}>

The items in source can also be 2-tuples, where the first item is the
enumeration value name and the second is the integer value to assign to the
value.  If 2-tuples are used, all items must be 2-tuples.

    >>> def enumiter():
    ...     start = 1
    ...     while True:
    ...         yield start
    ...         start <<= 1
    >>> make('Flags', zip(list('abcdefg'), enumiter()))
    <Flags {a: 1, b: 2, c: 4, d: 8, e: 16, f: 32, g: 64}>


Differences from PEP 354
========================

Unlike PEP 354, enumeration values are not defined as a sequence of strings,
but as attributes of a class.  This design was chosen because it was felt that
class syntax is more readable.

Unlike PEP 354, enumeration values require an explicit integer value.  This
difference recognizes that enumerations often represent real-world values, or
must interoperate with external real-world systems.  For example, to store an
enumeration in a database, it is better to convert it to an integer on the way
in and back to an enumeration on the way out.  Providing an integer value also
provides an explicit ordering.  However, there is no automatic conversion to
and from the integer values, because explicit is better than implicit.

Unlike PEP 354, this implementation does use a metaclass to define the
enumeration's syntax, and allows for extended base-enumerations so that the
common values in derived classes are identical (a singleton model).  While PEP
354 dismisses this approach for its complexity, in practice any perceived
complexity, though minimal, is hidden from users of the enumeration.

Unlike PEP 354, enumeration values can only be tested by identity comparison.
This is to emphasis the fact that enumeration values are singletons, much like
``None``.


Acknowledgments
===============

The ``flufl.enum`` implementation is based on an example by Jeremy Hylton.  It
has been modified and extended by Barry Warsaw for use in the `GNU Mailman`_
project.  Ben Finney is the author of the earlier enumeration PEP 354.


.. _`PEP 354`: http://www.python.org/dev/peps/pep-0354/

.. _enum: http://cheeseshop.python.org/pypi/enum/

.. _`GNU Mailman`: http://www.list.org
