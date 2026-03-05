# Put everything in modules

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

The class `DebugGame` takes an instance of `Game` to have access to all of the
`Game` data for debugging.

```python
@dataclass
class DebugGame:
    """Debug game code."""
    game: "Game"
```

While this will result in a working program, we lose the ability to do proper
type checking because we cannot `import Game` in submodule `debug_game.py`.
Similarly, we cannot run any unit tests in `gamelibs` that require `Game`.

The improved project structure is to move `game.py` into its own module,
perhaps a module named `src`. Then `gamelibs` could do `from src.game import Game`.

