#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Class examples
"""

from __future__ import annotations
from dataclasses import dataclass, field

class BoilerPlateVector:
    """The usual way to make a class for instantiation has the boilerplate __init__().

    >>> BoilerPlateVector().components
    [1, 2]

    >>> vec = BoilerPlateVector()
    >>> vec.components
    [1, 2]
    """
    def __init__(self) -> None:
        self.components = [1, 2]

class Vector:
    """Class as a global singleton.

    A Class can store data grouped with methods WITHOUT creating an instance!

    The class has some initial data in it:
    >>> Vector.components
    [1, 2]

    We can call the classes methods directly on that data:
    >>> Vector.sum()
    3

    Those methods can modify the data:
    >>> Vector.append(3.0)
    >>> Vector.components
    [1, 2, 3.0]
    >>> Vector.sum()
    6.0

    We can also directly write to that data:
    >>> components = [1, 2, 4]
    >>> Vector.components = components
    >>> Vector.components
    [1, 2, 4]

    Or we can hide the same operation behind an update function:
    >>> Vector.update([1, 3])
    >>> Vector.components
    [1, 3]
    """
    components: list[int | float] = [1, 2]  # <--- This is a class variable.

    @classmethod

    def update(cls, components: list[int | float]) -> None:
        """Update my components with new values."""
        cls.components = components

    @classmethod
    def append(cls, component: int | float) -> None:
        """Append a value to my components."""
        cls.components.append(component)

    @classmethod
    def sum(cls) -> int | float:
        """Return the sum of my components."""
        _sum: int | float = 0
        for n in cls.components:
            _sum += n
        return _sum


@dataclass
class AltVector:
    """Class for making instances.

    Turn this into a class that makes instances with the 'dataclass' decorator:

    1. Note that the syntax to define attribute 'components' is exactly the same!

    2. But classmethod sum() must turn into an instance method (no 'classmethod'
       decorator). Since this is a 'dataclass', the 'classmethod' decorator will
       treat the first argument as the class type, which does not have any
       attributes or methods, it is just a data type.

       When we remove the 'classmethod' decorator, the first argument refers to
       an instance, not the class. We could leave the argument name "cls" (the
       Python runtime doesn't care) but that would be confusing. Call it "self".

    3. The use of 'classmethod' in a 'dataclass' is to make a new constructor.
       from_list() is an example: it makes an instances from a list (this could
       be some other datatype that makes sense) instead of having to use the
       type of attribute 'components' (which also happens to be a list in this
       case).

    >>> vec = AltVector.from_list([1.0,2.0])
    >>> vec
    AltVector(components=[1.0, 2.0])
    >>> vec.sum()
    3.0

    >>> AltVector().components
    AltVector(components=[1, 2])
    """
    components: list[int | float] = field(default_factory=lambda: AltVector([1,2]))  # <--- This is an instance variable.

    def sum(self) -> int | float:
        """Return the sum of my components."""
        _sum: int | float = 0
        for n in self.components:
            _sum += n
        return _sum

    @classmethod
    def from_list(cls, components: list[int | float]) -> AltVector:
        """Return a Vector made from a list."""
        return cls(components)


if __name__ == "__main__":
    print(f"Running doctests in {__file__}")
    import doctest
    doctest.testmod()
