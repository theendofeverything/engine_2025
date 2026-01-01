# Unit Tests

## Use pytest to run docstring tests

You don't need any `tests.py` or `test_blah.py` files. Just run this command
and pytest will find all docstring tests:

```
$ pytest --doctest-modules --verbose
```

### Control pytest behavior

Stop after failing two tests:

```
	pytest --doctest-modules --verbose --maxfail=2
```

### Control doctest behavior

To set doctest option flags, see https://docs.pytest.org/en/4.6.x/doctest.html

Create a `.pytest.ini` file:

```
[pytest]
doctest_optionflags = NORMALIZE_WHITESPACE ELLIPSIS
```

Alternatively, you can use comments directly in the code to apply options to
individual tests. Doctest calls these "directives". See
file:///home/kelvin/.local/share/doc/python-3.14-docs-html/library/doctest.html#directives

```python
>>> print(list(range(20)))  # doctest: +NORMALIZE_WHITESPACE
[0,   1,  2,  3,  4,  5,  6,  7,  8,  9,
10,  11, 12, 13, 14, 15, 16, 17, 18, 19]

>>> print(list(range(20)))  # doctest: +ELLIPSIS
[0, 1, ..., 18, 19]
```

## Context on my usual flow

For context, I am used to writing a single script and using the
`if __name__ == '__main__'` block as the place to invoke `doctest`. That does
not work in a project.

Once files are laid out in a project, the `import` system and the linters both
fight you like whack-a-mole: you cannot satisfy both AND still have the
convenience of running an individual module as a script. One part of this setup
is always broken.

I emerge from this rabbit hole with the following wisdom: just use `pytest` to
run the docstring tests.

## Pursuing my usual flow down a rabbit hole

I am leaving the following sub-section here to document the rabbit hole of
abandoning my usual flow of running each module as its own script and instead
adopting `pytest` to run all my Python doctest unit tests.

### Use try/except to find modules inside lib

*You know you have taken a wrong turn if the basic `import` system seems to
require exception handling.*

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

Or do not put an executable `__main__` section in lib code and create a
top-level `tests.py` instead and call all the docstring tests from there?

Nope, you don't even need that. Just use `pytest --doctest-modules`.
