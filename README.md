# About

Use pygame to create an application.

# Why

I started this while working with Frank Palmer on our weekly Wednesday meetups.
We decided to implement the Fourier Transform to analyze audio data. First we
thing did was record some audito data and I insisted on writing my own data
plotting application.

# Roadmap

This will eventually turn into that data plotting application. At the moment it
is still in the early stage of just getting a basic UI to build on top of.

# Math

The coordinate transforms just use high-school algebra. These will be replaced
with matrix algebra using homogenous coordinates for translation.

# Python code

The Python project follows a simple structure. The project is essentially flat
with an entry point in `main.py` and all other code residing in the `engine/`
folder with the top-level code in `engine/game.py`:

```
.
├── main.py
├── engine
│   ├── __init__.py
│   ├── game.py <------------ TOP-LEVEL GAME CODE
│   ...
│   └── ui.py
├── .pylintrc
└── mypy.ini
```

The `engine/__init__.py` makes this folder a package.

*Note: Python runs the application just fine without this `__init__.py`. The
`__init__.py` is only necessary to avoid linter `mypy` throwing the error
`Cannot find implementation or library stub for module named ...`.*

Many of the `engine/` files are Python modules that define a single
class:

File                  | Class
----                  | -----
`engine/colors.py`    | `Colors`
`engine/coord_sys.py` | `CoordinateSystem`
`engine/game.py`      | `Game`
`engine/panning.py`   | `Panning`
`engine/renderer.py`  | `Renderer`
`engine/timing.py`    | `Timing`
`engine/ui.py`        | `UI`

Class `Game` contains the top-level game code. It is instantiated in `main.py`
where `Game().run()` launches the application. In the future, I might bump
`game.py` up out of the `engine/` folder and get rid of `main.py`. For now,
`main.py` is a convenient place to setup logging and register a `shutdown()`
function for cleanup when the application exits.

# Docs in `doc`

These docs are context for future me to remember the workflow, house-keeping
miscellany of developing a Python project.

- [Pygame Docs](doc/pygame_docs.md)
- [Vim](doc/vim.md)
- [Python Linters](doc/python_linters.md)
- [Unit Tests](doc/unit_tests.md)
- [Dataclasses](doc/dataclasses.md)
- [Type Hints](doc/type_hints.md)
