# Pygame Docs

* `;kpg` opens the local copy of the pygame docs in your browser (must activate
  the virtual environment where `pygame` is installed before launching Vim)
* `;KPG` opens the on-line copy of the pygame docs
* `;kpy` opens the local copy of the Python docs in your browser (must download
  the HTML Python docs manually, see my notes in `:h python.txt`)
* `;KPY` opens the on-line copy of the Python docs

## Details on opening pygame docs

Open `pygame/docs/generated/index.html` in your browser:

```vim
" This works if you added your virtualenv site-packages folder to your Vim path
:find pygame/docs/generated/index.html
" Now with the cursor in the buffer, use Vim shortcut ;html
```

From the command-line, `cd` into the virtualenv site-packages folder, then:

```
$ open pygame/docs/generated/index.html
```

Or use `pydoc` to open specific functions in your MANPAGER (my MANPAGER is Vim):

```
$ pydoc3 pygame
...
$ pydoc3 pygame.display
...
$ pydoc3 pygame.display.set_mode
```

# Vim

- `;mg`
    - Run the game (must be at project root level)
- `]m` `[m` `]M` `[M`
    - Navigate to start(`m`)/end(`M`) of next(`]`)/prev(`[`) function definition
- `;tp`
    - Make tags (must be at project root level)
    - Note: Vim omni completion does **not** use the tags file

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

If a Class has "too-many-instance-attributes", add this above the Class definition to disable the warning:

```python
# pylint: disable=too-many-instance-attributes
```

*Rationale*: It is early days in the codebase and you know you will refactor many of these attributes into their own class

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
