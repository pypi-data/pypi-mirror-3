

"""
typespec
========

typespec is two things:
    
1. A format specification for function annotations.

2. A module for parsing annotations that follow this specification.

The typespec format
-------------------

The typespec format uses standard Python data structures to specify object 
types. The following types are recognised:

* ``str`` - this is human readable documentation.

* ``type`` - this is a type/class that a conforming object may be an instance of. An object conforms to a typespec if it is an instance of one of the specified types or it passes validation of a validation class.

* ``tuple`` - this is a grouping of other strs, types and tuples. There is no semantic difference between grouped and ungrouped types but grouped strs are documentation that applies only to the types in the same grouping.

Other types are allowed but their meaning is undefined.

Simple Examples
~~~~~~~~~~~~~~~

Human readable documentation only - no type restrictions defined::

    "some description of a value"


A value that must be a string::

    str


A documented string value::

    (str, "description of the meaning of the string contents")


A value that may be a string or a number::

    (str, int, float)


A value that may be a string or a number with type specific documentation::

    (
        (str, "description of the meaning of the string contents"),
        (int, float, "what does the number represent?")
    )

Validation Classes
~~~~~~~~~~~~~~~~~~

Sometimes it is desirable to check more than just the type of an object.
For this purpose, validation classes can be defined and used in typespecs.
Validation classes are classes that have a ``__validate__`` method. 
Before an object is validated against a validation class, it is checked that
it is an instance of the base class (ValidationClass.__base__) of the 
validation class. In order to validate a value, the validation class is 
instantiated with that object as the only argument (so it should have an 
``__init__`` method definition like: ``def __init__(self, val):``) and then the 
``__validate__`` method is called on the resulting object. 
If this returns a true value, the object is deemed valid else it is deemed 
invalid.

Examples::

    class PositiveInt(int):
        def __validate__(self):
            return self > 0

    class PositiveFloat(float):
        def __validate__(self):
            return self > 0.0

    class PositiveNumber(object):
        def __init__(self, val):
            self.val = val

        def __validate__(self):
            if isinstance(self.val, int):
                return PositiveInt(self.val).__validate__()
            if isinstance(self.val, float):
                return PositiveFloat(self.val).__validate__()

    class SingleCharacterString(str):
        def __validate__(self):
            return len(self) == 1

Using typespecs in Annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A typespec can be used in function annotations. For argument annotations, it
specifies the type of argument. For return annotations it specifies the type
of object returned/yielded.

Examples::

    def add_chars(
        a : SingleCharacterString, 
        b : SingleCharacterString) -> SingleCharacterString:
        '''
        Adds the ordinal values of 2 characters and returns the character with
        that ordinal value.
        '''
        return chr(ord(a) + ord(b))

    def sum(a : (int, float), b : (int, float)) -> float:
        return float(a + b)

    def install_python(
        path : (str, "The file path that python should be installed to"),
        version : (str, "The version of python to install") = "3.2"
        ) -> (bool, "True if successful, False if unsuccessful"):
            #python installation code

    def ords(string : str) -> int:
        '''yields the ordinal values of the characters in ``string``.'''
        for c in string:
            yield ord(c)

The typespec module
-------------------

The typespec module provides simple utilities for validating values against
typespecs.

Basic Usage
~~~~~~~~~~~

Checking an object against a typespec::

    >>> #use the in operator
    >>> 1 in typespec.TypeSpec((int, float))
    True
    >>> "hello" in typespec.TypeSpec((int, float))
    False

Listing types in a typespec::

    >>> #simply iterate over the TypeSpec object
    >>> sorted(t.__name__ for t in typespec.TypeSpec((int, str, "doc")))
    ['int', 'str']

Accessing human readable documentation::

    >>> #use the doc method
    >>> typespec.TypeSpec("some documentation").doc()
    'some documentation'
    >>> my_spec = typespec.TypeSpec((
    ...     (str, "description of the meaning of the string contents"),
    ...     (int, float, "what does the number represent?")
    ... ))
    >>> my_spec.doc()
    ''
    >>> my_spec.doc(str)
    'description of the meaning of the string contents'
    >>> my_spec.doc(int)
    'what does the number represent?'
    >>> my_spec.doc(float)
    'what does the number represent?'

For more details see the module documentation.


"""

__version__ = '1.0.0'


def isa(
        obj : "The object to validate", 
        cls : (type, "The class to validate against.")
    ) -> (bool, "True for successful validation, False for failure."):
        """
        Check if an object is an instance of a type/class or if it passes
        validation of a validation class.
        """
        return (isinstance(obj, cls) or (isinstance(obj, cls.__base__) and
                    hasattr(cls, '__validate__') and
                    bool(cls(obj).__validate__())
                ) or False)


class TypeSpec(object):
    """
    Represents a typespec.
    """
    def __init__(self, spec):
        """
        Create a new TypeSpec object from an object ``spec`` that follows
        the typespec format. (note: if it doesn't follow the format, it
        will simply be ignored)
        """
        self._docs = []
        self._types = {}
        if isinstance(spec, tuple):
            self._add(*spec)
        else:
            self._add(spec)

    def _add(self, *args):
        n = len(self._docs)
        self._docs.append("")
        for arg in args:
            if isinstance(arg, str):
                self._docs[n] += arg
            elif isinstance(arg, type):
                self._types[arg] = n
            elif isinstance(arg, tuple):
                self._add(*arg)

    def doc(self, 
            typ : (type, "A type/class to get documentation for.") = None
        ) -> (str, "The documentation."):
        """
        Return the documentation for a particular type/class ``typ``.
        If ``type`` is not specified, the general documentation will be
        used.
        This will cause an error if the type is not in the typespec.
        """
        if typ:
            return self._docs[self._types[typ]]
        else:
            return self._docs[0]

    def __iter__(self):
        """
        Iterate over the types in the typespec.
        """
        return iter(self._types)

    def __contains__(self, obj : "Object to be validated.") -> (
            bool, "True if ``obj`` passes validation, False if it fails."):
        """
        Validate a value against the typespec.
        """
        if len(self._types) == 0:
            return True
        for t in self:
            if isa(obj, t):
                return True
        return False



