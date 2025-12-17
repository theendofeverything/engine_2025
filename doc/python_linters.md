# Python linters

## mypy - type checking

Type checking is great, but it was bolted onto Python, so there are annoying issues.

`lib/geometry_types.py` defines `Point2D` and `Vec2D`. Both classes have a
method that converts to the other class. `Point2D` has `as_vec()` and `Vec2D`
has `as_point`:

```python
@dataclass
class Point2D:
    ...
    def as_vec(self) -> Vec2D:
        ...

@dataclass
class Vec2D:
    ...
    def as_point(self) -> Point2D:
        ...
```

Whichever class I define first in the file is not going to know about the other
one because it is not defined yet!

Fix this problem with this one-liner:

```python
from __future__ import annotations
```

## pylint - too few public methods

If a Class has "too few public methods", add this above the Class definition to
disable the warning:

```python
# pylint: disable=too-few-public-methods
```

*Rationale*: It is early days in the codebase and you know you will add methods
to this class but haven't written that code yet and just need to silence this
warning for now.

If you do not plan on adding more public methods, turn this into a `dataclass`:

```python
from dataclasses import dataclass

@dataclass
class Vec2D:
    """Two-dimensional vector.
    """
    x: float
    y: float

    @classmethod
    def from_points(cls, start: Point2D, end: Point2D) -> Vec2D:
        """Create a vector from two points: vector = end - start."""
        return cls(x=end.x-start.x,
                   y=end.y-start.y)
```

## pylint - too many instance attributes

If a Class has "too many instance attributes", add this above the Class definition to disable the warning:

```python
# pylint: disable=too-many-instance-attributes
```

*Rationale*: It is early days in the codebase and you know you will refactor
many of these attributes into their own class

## flake8 undefined name

If module A uses module B but module B acts on a type defined in module A, I
have to import module A, otherwise the type is undefined:

```python
# engine/game.py
from .geometry_operators import CoordinateTransform

class Game:
    ...

# engine/geometry_operators.py
class CoordinateTransform:
    def __init__(self, game: Game) -> None:
        ...
```

`pylint` throws the error:

```
engine/geometry_operators.py|10 col 29| E0602: Undefined variable 'Game' (undefined-variable)
```

But if I import `Game` into `geometry_operators`:

```python
# engine/geometry_operators.py
from .game import Game
```

Then I have a cyclic import:

```
engine/panning.py|1| R0401: Cyclic import (engine.game -> engine.geometry_operators) (cyclic-import)
```

It's not really a circular dependency since I only need the type for type
checking. (Python's run time is all duck-typed: it does not actually need to
know the type that module B is acting on.)

The only way to eliminate the cyclic import is to put these classes in the same
file. Instead, put the type name in quotes. This works just
fine except that `flake8` complains "undefined name":

```
lib/geometry_operators.py|10 col 30| F821 undefined name 'Game'
```

So I tell `flake8` to ignore error F821 in the `lint` recipe of the `Makefile`:

```
-flake8 --max-complexity 10 --max-line-length 100 --extend-ignore F821
```

And I add this to `g:ale_python_flake8_options` in my `vimrc`:

```vim
let g:ale_python_flake8_options = '--max-line-length 100 --extend-ignore F821'
```

## Use try/except to find modules inside lib

When running a file on its own inside `lib` for testing purposes, this import
statement does not work because we are already inside `lib`:

```python
from lib.geometry_types import Point2D
```

The solution is to use `try/except` clause like this:

```python
try:
    from .geometry_types import Point2D
except ModuleNotFoundError:
    from lib.geometry_types import Point2D
```

Unfortunately, to run a `lib/thing.py` as a script, the import has to be absolute:

```python
    # Note no leading dot in front of geometry_types
    from geometry_types import Point2D
```

The `doctest` module is fine with this and most of the linters are fine with
this. The one exception is `mypy`. Now it complains about missing imports.

This is just a nuisance warning. Silence it by creating a `mypy.ini` file in the project root:

```
[mypy]
disable_error_code = import-not-found
```

Or do not put an executable `__main__` section in lib code and create a top-level `tests.py` instead.

