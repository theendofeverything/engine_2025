# About

Use pygame to create an application.

# Setup

Install `pygame` (for talking to the OS).

Then launch the application:

```
$ make run
```

This does:

```
$ ./main.py
```

## Optional setup

Install `pytest` (to run the doctests), and the linters `mypy`, `pycodestyle`,
and `pylint`.

Run the tests:

```
$ make tests
```

This does:

```
$ pytest --doctest-modules --verbose
```

Run the linters:

```
$ make lint
```

This does:

```
$ pycodestyle --max-line-length=100 .
$ pylint .
$ mypy --strict .
$ flake8 --max-complexity 10 --max-line-length 100 --extend-ignore F821 .
```

# Why

This started out from a desire to make a plotting application. See
private repo https://github.com/theendofeverything/pygame-kata-2025_11_17.

It ended up being my first time implementing coordinate transforms where I felt
I really understood all of the underlying math. So I decided to keep going on
the graphics engine part.

# Roadmap

I started out only doing 2D graphics, but now that I understand the math, I
realize it isn't a big leap to turn this into a 3D engine.

I have a basic UI to build on top of. Now I am working on getting more graphics
onto the screen.

# Math

The coordinate transforms use matrices as the transform operators. The matrix
dimensions are one larger than the number of spatial dimensions to use
homogeneous coordinates for translation. See
[doc/coordinate_transforms.md](doc/coordinate_transforms.md).

# Python code

The Python project follows a simple structure. The project is essentially flat
with an entry point in `main.py` and all other code residing in the `engine/`
folder with the top-level code in `engine/game.py`:

```
.
├── doc
├── engine
│   ├── ...
│   ├── game.py <-------------- TOP LEVEL GAME CODE
│   ├── ...
│   ├── __init__.py <---------- MAKES engine A PACKAGE
│   ├── ...
│   ...
├── main.py <------------------ ENTRY POINT
├── Makefile <----------------- RECIPES FOR LINTING, TESTING, AND TAGGING
├── .mypy.ini <---------------- LINTING CONFIGURATION
├── .pylintrc <---------------- LINTING CONFIGURATION
├── .pytest.ini <-------------- TESTING CONFIGURATION
└── README.md
```

The `engine/__init__.py` makes this folder a package.

*Note: Python runs the application just fine without this `__init__.py`. The
`__init__.py` is only necessary to avoid linter `mypy` throwing the error
`Cannot find implementation or library stub for module named ...`.*

Many of the `engine/` files are Python modules that define a single
class. Some modules define additional classes, but the API is in the one class
the file is named after.

File                  | Class
----                  | -----
`engine/art.py`       | `Art`
`engine/colors.py`    | `Colors`
`engine/coord_sys.py` | `CoordinateSystem`
`engine/debug.py`     | `Debug`
`engine/game.py`      | `Game`
`engine/panning.py`   | `Panning`
`engine/renderer.py`  | `Renderer`
`engine/timing.py`    | `Timing`
`engine/ui.py`        | `UI`

The other engine files define multiple classes used in the application:

File                           | Classes
----                           | -------
`engine/drawing_shapes.py`     | `Line2D`, `Cross`
`engine/geometry_operators.py` | `Matrix2D`, `Matrix2DH`, `Matrix3D`
`engine/geometry_types.py`     | `Point2D`, `Vec2D`, `Vec2DH`, `Vec3D`
`log.py`                       | No class, just function `setup_logging()`

Class `Game` contains the top-level game code. It is instantiated in `main.py`
where `Game().run()` launches the application. In the future, I might bump
`game.py` up out of the `engine/` folder and get rid of `main.py`. For now,
`main.py` is a convenient place to setup logging and register a `shutdown()`
function for cleanup when the application exits.

# Docs in `doc`

These docs are context for future me to remember the workflow, house-keeping
miscellany of developing a Python project.

- [Coordinate transform math](doc/coordinate_transforms.md)
- [Dataclasses](doc/dataclasses.md)
- [Python str format specifiers](doc/format_specifiers.md)
- [Python pattern matching](doc/pattern_matching.md)
- [Pygame docs](doc/pygame_docs.md)
- [Python linters](doc/python_linters.md)
- [Type hints](doc/type_hints.md)
- [Unit Tests](doc/unit_tests.md)
- [Vim](doc/vim.md)
