# About

Use pygame to create an application.

Folder `engine` is my 2D engine Python package. `game_template.py` is a
starting point for writing a `game.py`.

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

![screenshot](doc/img/screenshot-2025-12-25.png)

- Mouse wheel zoom/pan
- `q`: Quit
- `c`: Clear debug snapshot artwork
- `Space`: Toggle debug art overlay
- `d`: Toggle debug hud
- `Ctrl_+`: Increase debug HUD font
- `Ctrl_-`: Decrease debug HUD font
- Resize the window with a mouse click-drag

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

## Engine structure

The Python project follows a simple structure. The project is essentially flat
with an entry point in `main.py`, the game in `game.py`, and all engine code
residing in the `engine/` folder:

```
.
├── doc
├── engine
│   ├── __init__.py <---------- MAKES engine A PACKAGE
│   ├── ...
│   ...
├── game.py <------------------ TOP LEVEL GAME CODE
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

## Use engine for a game

My quick and dirty way to use the engine is to create symbolic links. I know
engine will change as I develop game code and rather than deal with git
submodules, I am just going to use symbolic links and update the git repos
separately.

I clone `engine_2025`. Then I make a new folder, I make a link to `setup.sh` in
my new folder and run the `setup.sh`:

```
$ mkdir my_project && cd my_project
$ ln -rs ../engine/setup.sh
$ ./setup.sh
```

This results in the following project structure for my game:

```
.
├── doc -> ../engine_2025/doc
├── engine -> ../engine_2025/engine
├── game.py
├── .gitignore
├── main.py -> ../engine_2025/main.py
├── Makefile -> ../engine_2025/Makefile
├── .mypy.ini
├── .pylintrc
├── .pytest.ini
├── README.md
└── setup.sh -> ../engine_2025/setup.sh
```

`game_template.py` is the starting point -- the `setup.sh` renames this to
`game.py`. If you name it something other than `game.py`:

- make a local copy of `main.py` and delete the symbolic link
- edit the module name in `main.py` to import `Game` from the new name

```python
# main.py
from game import Game
```

## Engine contents

Many of the `engine/` files are Python modules that define a single
class. Some modules define additional classes, but the API is in the one class
the file is named after.

File                  | Class
----                  | -----
`engine/art.py`       | `Art`
`engine/colors.py`    | `Colors`
`engine/coord_sys.py` | `CoordinateSystem`
`engine/debug.py`     | `Debug`
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

The root-folder contains a `main.py` and `game.py`. The `game_template.py` is
just a starting point for writing a `game.py`.

`main.py` is not specific to any game. It just sets up logging, registers a
`shutdown()` function for cleanup on exit, and launches the game code.

Class `Game` contains the top-level game code. It is instantiated in `main.py`
where `Game().run()` launches the application.

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
