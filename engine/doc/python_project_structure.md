Could `Game` depend on prototypes of its data structures and methods in another
module that everyone imports from, including `Game` itself?

# Dependency Injection Project Structure

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

There are two workarounds.

First, we can make 'Game' responsible for instantiating Global Singletons of
whatever is in `engine` and `gamelibs` and then as part of the
`Game.__init__()` or `Game.__post_init__()` (depending on whether the Global
Singletons require setup prior to instantiation), `Game` instantiates those
classes and passes an instance of itself (`self`) to those classes as a first
argument. Those Global Singletons now have a handle on the `Game` Global
Singleton. This is one of way doing *Dependency Injection* in Python. This will
work regardless of the project structure, so if you really like having `game`
sit in the root folder, then this is a reasonable way to go.

Second, we can alter the project structure by adding a `src` module
that is a sibling with `engine` and `gamelibs`. If we put `game` inside `src`,
we gives `engine` and `gamelibs` access to `game` via `from src.game import
Game`. But we still will not be able to import `Game` into any of these modules
because that will create circular dependencies. So 



The workaround is called *Dependency Injection*. We make a Global Singleton of
`Game` that is passed into the constructor of anything that needs access to
`Game`. In fact, this circular import issue is one of two reasons for making
`Game` a class instead of just using the Python module `game.py` itself as the
namespace for other modules that need access to `game` stuff. (The other
reason, which we'll explore more in a later section, is that linters heavily
discourage a style that exposes global mutable variables, unless those global
mutables are dictionaries.)

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

This is Dependency Injection. It will result in a working program and it is
considered by some to be the best way to structure the project.

But we lose the ability to do proper type checking because we cannot
`import Game` in submodule `debug_game.py` to use `Game` for type-checking.

We also lose the ability to run any unit tests in `gamelibs` that require
`Game`.

# Put Everything in a Module

Put everything in modules, even the main `Game` code.

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
`context.py`, which does not import anything, so any other module can import
`context`.

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
    ├── context.py <-------- ADD THIS
    ├── coord_sys.py <--- imports core
    ├── renderer.py <---- imports core
    └── ui.py <---------- imports core
```

We can do this a few ways.

## Module as Namespace Class

In Python, modules are already singletons. They are initialized once and cached
in sys.modules. Instead of a complex class, you can put your global state in a
separate file: `context.py`.

In this approach, `context.py` is a context. `Game` writes itself to a global in
`context.py`.

```python
# context.py
game_handle = None
```

```python
# game.py
import context

class Game:
    def __init__(self):
        context.game_handle = self  # We don't need to pass instances of `Game` anymore
```

And at this point, `Game` can also stop being a class (if we know how the
syntax for working with modules in our program):

```python
# game.py
import context

context.game_handle = ?  # How do I talk about THIS module?
```

I have not tried this approach yet. I skipped straight to the next approach.

One disadvantage of this approach is that you lose a little control over the
name of the Namespace Class. The name becomes the module name.

For example, I defined Namespace Class `Mouse` in module `engine/mouse.py`. User code did:

```python
from engine.mouse import Mouse
...
Mouse.blah
```

And the doctests in `mouse.py` used `Mouse.blah`:

```python
>>> Mouse.is_pressed(ButtonName.LEFT)
False
```

When I pulled all of the members out of `Mouse` up to the module level, user code changed to:

```python
from engine import mouse
...
mouse.blah
```

And my doctests in `engine/mouse.py` changed to:

```python
>>> from engine import mouse
>>> mouse.is_pressed(mouse.ButtonName.LEFT)
False
```

So this all worked fine for `Mouse`, but it did not work for `Panning`. And not
because of circular imports. The code runs, but the linter does not like it.

```python
import pygame
from src.context import Context, namespace
from .geometry_types import Vec2D, Point2D


@namespace
class Panning:
    """Track mouse panning state.

    Attributes:
        is_active (bool):
            Panning is in two states: either active (is_active=True) or inactive
            (is_active=False).
        begin (Point2D):
            Position in the pixel coordinate system when panning transitioned to
            the active state. While in the active state, 'begin' does not
            change.
        end (Point2D):
            Latest mouse position in the pixel coordinate system while panning:
            the game loads 'end' with the mouse position on every iteration of
            the game loop.
        vector (Vec2D):
            Amount of mouse pan, obtained from end - begin.
            The 'Panning.vector()' is picked up during rendering, as follows:
                When the game loop renders drawing entities, it converts entity
                coordinates from GCS to PCS:
                    coord_sys.xfm(v:Vec2D, coord_sys.matrix.gcs_to_pcs)

                That coordinate transform matrix is calculated using the origin
                offset vector:
                    coord_sys.translation

                And coord_sys.translation is calculated using the
                'Panning.vector()' (this attribute).

    >>> mouse_pos = (123, 456)                          # Position when button 1 was pressed
    >>> Panning.begin = Point2D.from_tuple(mouse_pos)   # Track panning begin position
    >>> mouse_pos = (246, 456)                          # Position later while still panning
    >>> Panning.end = Point2D.from_tuple(mouse_pos)     # Track latest panning position
    >>> Panning.vector()                                # Report the latest panning vector
    Vec2D(x=123, y=0)
    """
    begin:                  Point2D = Point2D(0, 0)     # Dummy initial value
    end:                    Point2D = Point2D(0, 0)     # Zero-out the panning vector
    is_active:              bool = False

    @classmethod
    def vector(cls) -> Vec2D:
        """Return the panning vector: describes amount of mouse pan."""
        return Vec2D.from_points(start=cls.begin, end=cls.end)

    @classmethod
    def start(cls, position: tuple[int | float, int | float]) -> None:
        """User started panning."""
        panning = cls
        panning.is_active = True
        panning.begin = Point2D.from_tuple(position)

    @classmethod
    def stop(cls) -> None:
        """User stopped panning."""
        panning = cls
        panning.is_active = False
        # game.coord_sys.pcs_origin = game.coord_sys.translation.as_point()  # Set new origin
        # Set new origin
        Context.game.coord_sys.pcs_origin = Context.game.coord_sys.translation.as_point()
        panning.begin = panning.end  # Zero-out the panning vector

    @classmethod
    def update(cls) -> None:
        """Update 'panning.end': the latest point the mouse has panned to.

        Dependency chain depicting how panning manifests as translating the game
        view on the screen:
            renderer <-- coord_sys.matrix.gcs_to_pcs <-- coord_sys.translation <-- Panning.vector()

            In the above dependency chain:
                - read "<--" as "thing-on-left uses thing-on-right"
                - Panning.vector() = Panning.end - Panning.begin
        """
        panning = cls
        if panning.is_active:
            mouse_pos = pygame.mouse.get_pos()
            panning.end = Point2D.from_tuple(mouse_pos)

```

This is the module-level namespace class version of `Panning`:

```python
import pygame
from src.context import Context
from .geometry_types import Vec2D, Point2D


begin:     Point2D = Point2D(0, 0)     # Dummy initial value
end:       Point2D = Point2D(0, 0)     # Set equal to begin to zero-out the panning vector
is_active: bool = False


def vector() -> Vec2D:
    """Return the panning vector: describes amount of mouse pan."""
    return Vec2D.from_points(start=begin, end=end)


def start(position: tuple[int | float, int | float]) -> None:
    """User started panning."""
    global is_active, begin
    is_active = True
    begin = Point2D.from_tuple(position)


def stop() -> None:
    """User stopped panning."""
    global begin, is_active
    is_active = False
    # game.coord_sys.pcs_origin = game.coord_sys.translation.as_point()  # Set new origin
    # Set new origin
    Context.game.coord_sys.pcs_origin = Context.game.coord_sys.translation.as_point()
    begin = end  # Zero-out the panning vector


def update() -> None:
    """Update 'panning.end': the latest point the mouse has panned to.

    Dependency chain depicting how panning manifests as translating the game
    view on the screen:
        renderer <-- coord_sys.matrix.gcs_to_pcs <-- coord_sys.translation <-- Panning.vector()

        In the above dependency chain:
            - read "<--" as "thing-on-left uses thing-on-right"
            - Panning.vector() = Panning.end - Panning.begin
    """
    global end
    if is_active:
        mouse_pos = pygame.mouse.get_pos()
        end = Point2D.from_tuple(mouse_pos)

```

The keyword `global` is necessary to tell Python we are talking about the
module-level variables, not local variables.

The linter has two complaints with this code:

- Constant name `is_active` doesn't conform to `UPPER_CASE` naming style (invalid-name)
- Using the global statement (global-statement): *it flags every line that uses `global`*

I'm not sure what the people who write the linter rules would consider the
correct way to use a module. It is weird to me that `Mouse` avoids these issues
but `Panning` does not. It is not clear to me what the difference is.

## Context as a Global Singleton Hub Class

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

## Namespace Classes

A Namespace Class is a class that is never instantiated. It just exists for
grouping data and functions together.

It is almost exactly like a Global Singleton, except we need to make all of the
methods either `@staticmethod` or `@classmethod`. This removes the boilerplate
need to instantiate and decide where the instance lives, though now that we
have our `Context` class, it is clear where the instance lives, so this is not
a huge win. But it is still nice to skip the step of making an instance.
Another benefit is we can encode our intent that there are not multiple
instances of this data structure. Since we do not need to instantiate, we can
define an `__init__()` method that throws an error if we forget and try to
instantiate this class.

To make it easier to use the Namespace Class design pattern, we can make our
own `@namespace` decorator:

```python
from typing import Type, TypeVar, Any
T = TypeVar("T")

def namespace(cls: Type[T]) -> Type[T]:
    """Class decorator to identify a Namespace Class (a class that cannot be instantiated)."""

    def no_init(self: Any) -> None:
        """Prevent instantiation"""
        raise RuntimeError(f"{cls.__name__} is a Namespace Class and cannot be instantiated.")

    setattr(cls, "__init__", no_init)
    return cls
```

And then we use it like any other decorator:


```python
from .context import Context, namespace

@namespace
class Game:
    ...
```

Built-in function `settatr()` assigns an existing attribute or creates a new
attribute. But if it is a new attribute, the linter will later complain that
the attribute does not exist, even though the program will run just fine.

Member `__init__` exists by default because `Game` is a class. The python
linter will NOT throw an error that `__init__()` does not exist.

But if we use this same method to add a new member, such as `state()`, the
python linter will throw an error. We can avoid the linter error by adding a
placeholder definition of `state` in any class that has this decorator. While
strictly not necessary, this is a nice reminder that the method exists (and
this prevents us from accidentally making a method with the same name, only to
have it silently overwritten).

Here are two new methods for our `@namespace` decorator to add:

```python
def namespace(cls: Type[T]) -> Type[T]:

    ...

    def state() -> str:
        """Return pretty string of class public members and their values."""
        public_members = {
                k: v for k, v in cls.__dict__.items()
                if not callable(getattr(cls, k))
                and not k.startswith("_")
                }
        strings = [f"{k}={v}" for k, v in public_members.items()]
        return f"State: {cls.__name__}({', '.join(strings)})"

    def api() -> str:
        """Return pretty string naming class public members and methods."""
        public_members = [x for x in dir(cls)
                          if not callable(getattr(cls, x))
                          and not x.startswith("_")
                          ]
        public_methods = [fn for fn in dir(cls)
                          if callable(getattr(cls, fn))
                          and not fn.startswith("_")]
        member_strings = [f"{x}" for x in public_members]
        method_strings = [f"{fn}()" for fn in public_methods]
        return f"API for {cls.__name__}: {', '.join(member_strings)}, {', '.join(method_strings)}"

    ...
    setattr(cls, "state", state)
    setattr(cls, "api", api)
```

And here are the empty methods added to `Game` to avoid the linter error:

```python
@namespace
class Game:
    ...
    @classmethod
    def state(cls) -> None:
        """Defined in namespace: string representation of public members and their values"""

    @classmethod
    def api(cls) -> None:
        """Defined in namespace: string representation of public members and public methods"""
```

Now we can do this to inspect `Game`:

```python
    print(Game.state())
    print(Game.api())
```

- `state()` is helpful for inspecting values
- `api()` is helpful to remind us what the public API is (put this right into a docstring)

Now that `Game` is a Namespace Class and not a Global Singleton, how does that
affect registering it with `Context`? It doesn't, apart from naming variables slightly differently to make the intent clear:

```python
from typing import Type, TypeVar, Any
T = TypeVar("T")

@namespace
class Context:
    game: "Game" = None

    @classmethod
    def register_game(cls, game_class: Type[T]) -> None:
        """Load global handle to the instance of Game"""
        cls.game = game_class
```

We added the `@namespace` decorator to `Context` because it is also a Namespace
Class. Again, we do not *need* the decorator. All it is doing at this point is
preventing us from accidentally instantiating the class.

The bigger change is in `Game`. It's the usual transformation we would do when
a Global Singleton becomes a Namespace Class (again, nothing to do with our
decorator, this is just the design pattern).

The first step is to turn as many `Game` methods into `@staticmethod` as
possible. If we are just grouping functions inside `Game` for clarity, we
should use the decorator to make that clear.

Then all the remaining methods do depend on data in `Game`. So we make these
`@classmethods`.

There is no longer an `__init__()` or a `__post_init__()`. (There is an
`__init__()` thanks to our `@namespace` decorator, but all it does is thrown an
error).

So what used to be a `@dataclass` is now a `@namesapce`. I change the name of
`__post_init__()` to `setup()`:

```python
from .context import Context, namespace

@namespace
class Game:
    debug_font: str = "fonts/ProggyClean.ttf"
    entities:   dict[str, Entity] = {}
    coord_sys:  CoordinateSystem

    @classmethod
    def setup(cls) -> None:
        """Setup game state. Return a str for checking Game state in a unit test."""
        Context.register_game(cls)  # Global access to instance of Game()
        ...
```

An advantage of the Namespace Class pattern is we can drop all the
`dataclasses.field()` stuff (because we never instantiate). So, for example, we
can just say `Game` has an empty `dict` of `entities`.

An advantage of the Global Singleton pattern is that the `@dataclass` decorator
gets us a nice `__repr__()` for free. Surely we can do that ourselves?

Not quite. I added a `__repr__()` to my `@namespace` decorator, but
`__repr__()` does not work for classes, only for objects! In other words,
`print(Game)` just prints the address of the `Game` class. There is no Python
syntactic sugar for a class `__repr__()`.

Of course, we can still call `Game.__repr__()`, but at that point I may as well
name this function something meaningful rather than misuse a Python name. So I
call it `state_str()`:

```python
import inspect
from typing import Type, TypeVar, Any
T = TypeVar("T")

def namespace(cls: Type[T]) -> Type[T]:
    ...
    def state_str() -> str:
        """Return pretty string of public class members."""
        attrs = {
            k: v for k, v in cls.__dict__.items()
            if not k.startswith("_")
            and not inspect.isroutine(v)
            and not isinstance(v, (classmethod, staticmethod))
        }
        items = [f"{k}={v!r}" for k, v in attrs.items()]
        return f"{cls.__name__}({', '.join(items)})"

    setattr(cls, "state_str", state_str)
    return cls
```
