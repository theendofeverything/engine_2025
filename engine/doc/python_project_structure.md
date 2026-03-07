# Dependency Injection Project Structure

Put everything in modules, even the main `Game` code.

Say we have a module named `engine` which contains submodules `art.py` and
`colors.py`:

```
.
├── engine
│   ├── art.py
│   ├── colors.py
│   ├── __init__.py
│   ...
```

Submodule `art` uses submodule `colors` like this:

```python
from .colors import Colors
```

Say we have another module named `gamelibs` which contains `debug_game.py`:

```
.
├── engine
│   ...
├── gamelibs
│   ├── debug_game.py
│   ├── __init__.py
```

Submodule `debug_game.py` uses `engine.colors` like this:

```python
from engine.colors import Colors
```

Now consider this structure for a project that uses modules `engine` and
`gamelibs` in `Game`.

```
.
├── engine
│   ...
├── gamelibs
│   ├── debug_game.py
│   ├── __init__.py
│   ...
├── game.py
```

The class `Game` in `game.py` uses anything from modules `engine` and
`gamelibs` with no problem. But submodules `engine` and `gamelibs` do not have
access to `game`.

The workaround is called *Dependency Injection*.

For example, the class `DebugGame` in submodule `gamelibs.debug_game` takes an
instance of `Game` to have access to all of the `Game` data for debugging.

```python
@dataclass
class DebugGame:
    """Debug game code."""
    game: "Game"
```

And `Game` in `game.py` instantiates `DebugGame` and passes itself in the `__post_init__()`:

```python
@dataclass
class Game:
    ...
    debug_game: DebugGame = field(init=False)
    ...

    def __post_init__(self) -> None:
        ...
        self.debug_game = DebugGame(game=self)
```

This will result in a working program and many people consider this the best way to structure the project.

But we lose the ability to do proper type checking because we cannot
`import Game` in submodule `debug_game.py` to use `Game` for type-checking.

We also lose the ability to run any unit tests in `gamelibs` that require
`Game`.

# Singleton Hub Project Structure

Since `engine` and `gamelibs` have no problem importing from each other, what
if we do the same with `game.py`: put this in a module named `src`.

If we put everything in modules, any modules will be able to import from any
other module.

```
.
├── main.py
├── src
│   ├── __init__.py
│   └── game.py
├── gamelibs
│   ├── __init__.py
│   └── debug_game.py
└── engine
    ├── __init__.py
    ├── ...
    └── ui.py
```

Note that this project structure also works with Dependency Injection (the
strategy in the previous section).

But the moment we try to actually take advantage of the visibility of `game.py`
to `engine` and `gamelibs`, we run into the circular import problem.

In modules `gamelibs` and `engine`, we do this:

```python
from src.game import Game
```

But when we try to run the program, we get a circular import. For example,
`Game` uses `DebugGame` and `DebugGame` uses `Game`.

If the imports happen at the top of the submodule files (`src/game.py` and
`gamelibs/debug_game.py`), we have a circular import: the first use of `Game`
needs to import `DebugGame`, which means we are using `DebugGame`, but
`DebugGame` needs to import `Game`, which we are already in the middle of
importing!

This might be fixed with lazy imports (moving the `import` statement into the
class where the module is actually needed), but this can get messy too.
Lazy imports are a quick fix, not a tool for structuring projects.

The solution is subtle and not obvious. We add a submodule to `engine` named
`core.py`.

```
.
├── main.py
├── src
│   ├── __init__.py
│   └── game.py <-------- imports core
├── gamelibs
│   ├── __init__.py
│   └── debug_game.py <-- imports core
└── engine
    ├── __init__.py
    ├── core.py <-------- ADD THIS
    ├── coord_sys.py <--- imports core
    ├── renderer.py <---- imports core
    └── ui.py <---------- imports core
```

We can do this a few ways.

## Module as Global Singleton Hub

In Python, modules are already singletons. They are initialized once and cached
in sys.modules. Instead of a complex class, you can put your global state in a
separate file: `core.py`.

In this approach, `core.py` is a context. `Game` writes itself to a global in
`core.py`.

```python
# core.py
game_handle = None
```

```python
# game.py
import core

class Game:
    def __init__(self):
        core.game_handle = self  # We don't need to pass instances of `Game` anymore
```

I have not tried this approach yet. I skipped straight to the next approach.

## Class as Global Singleton Hub

It feels a little cleaner to put all this in a class rather than have just this
one thing in our project that relies on a different method of organizing data.

I make `src/context.py`:

```python
# pylint: disable=too-few-public-methods
class Context:
    """Global context."""
    game: "Game" = None

    @classmethod
    def register_game(cls, instance: "Game") -> None:
        """Load global handle to the instance of game"""
        cls.game = instance
```

This file imports nothing. But `game.py` and any submodule in `engine` or
`gamelibs` that needs global data imports `Context`.

## Advantages

However you choose to structure it, the advantages are the same.

`Game` used to have lots of members like this where I needed to postpone their
initialization to the `__post_init__()` so I could pass `self`:

```python
@dataclass
class Game:
    ...
    renderer:   Renderer = field(init=False)
    ...

    def __post_init__(self) -> None:
        ...
        self.renderer = Renderer(game=self)
        ...
```

And `Renderer()` took `game` as a required argument:

```python
@dataclass
class Renderer:
    game: "Game"
```

Now with `context`, `Renderer` does not require `game`. Within `Renderer` I
just `from src.context import Context` and use `Context.game`.

```python
from src.context import Context

@dataclass
class Renderer:
    ...
    def render_shapes(self) -> None:
        """Render GCS shapes to the screen."""
        game = Context.game
        ...
```

`Game` also imports `Context` with `from .context import Context`. `Game` no
longer needs a special `__post_init__()` for `Renderer`. It just registers
itself with the global singleton `Context` in the `__post_init__()`:

```python
from .context import Context
@dataclass
class Game:
    ...
    renderer:   Renderer = Renderer()
    ...
    def __post_init__(self) -> None:
        Context.register_game(self)
```
