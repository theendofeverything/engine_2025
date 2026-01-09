# What is a dataclass?

https://docs.python.org/3/library/dataclasses.html

```python
from dataclasses import dataclass
```

`dataclass` is a class decorator:

```python
@dataclass
class Colors:
    """Color names

    Use as a name-spaced constant:
    >>> Colors.text
    (255, 255, 255, 255)

    Or create an instance and use as a constant:
    >>> colors = Colors()
    >>> colors.text
    (255, 255, 255, 255)
    """
    background:     Color = Color(30, 60, 90)
    line:           Color = Color(120, 90, 30)
    line_debug:     Color = Color(200, 50, 50)
    text:           Color = Color(255, 255, 255)
```

The decorator `@dataclass` is just syntactic sugar to handle a lot of boiler
plate `class` code. Among other things, it creates the `__init__()` and
`__repr__()` methods.

This is the closest syntax Python has to making a simple C-style struct. That
is it's main use, but the `@dataclass` decorator also makes sense sometimes for
more typical Python classes.

# Why do I keep using dataclasses?

## Structs

I make a class a `dataclass` when I want something like a C struct:

```python
@dataclass
class Point2D:
    """Two-dimensional point."""
    x: float
    y: float
```

## Grouping instance variables

I make a class a `dataclass` when I want to group related instance variables
under a single class:

```python
@dataclass
class Debug:
    """Debug messages in the HUD and debug artwork."""
    hud:                    DebugHud = DebugHud()
    art:                    DebugArt = DebugArt()
```

In the above example, instantiating `debug=Debug()` gives me instances
`debug.hud` and `debug.art`.

## Enforced organization

I make a class a `dataclass` when I want to artificially constrain myself so
that I am forced (by Python) to organize my code better (examples below):

```python
class Game:
    """Game data is shared by all the code"""
    # Instance variables defined in the implicit __init__()
    debug:      Debug = Debug()     # Display debug prints in HUD and overlay debug art
    timing:     Timing = Timing()   # Set up a clock to set frame rate and measure frame period
    art:        Art = Art()         # Set up all artwork for rendering

    # Instance variables defined in __post_init__()
    ui:         UI = field(init=False)                  # Keyboard, mouse, panning, zoom
    coord_sys:  CoordinateSystem = field(init=False)    # PCS and GCS
    coord_xfm:  CoordinateTransform = field(init=False)
    renderer:   Renderer = field(init=False)

    def __post_init__(self) -> None:
        # Load pygame
        pygame.init()
        pygame.font.init()
        # Handle all user interface events in ui.py (keyboard, mouse, panning, zoom)
        self.ui = UI(game=self, panning=Panning())
        # Set the window size and center the GCS origin in the window.
        self.coord_sys = CoordinateSystem(
                panning=self.ui.panning,
                window_size=Vec2D(x=60*16, y=60*9))
        # Create 'coord_xfm' for transforming between coordinate systems
        self.coord_xfm = CoordinateTransform(coord_sys=self.coord_sys)
        # Handle rendering in renderer.py
        self.renderer = Renderer(
                game=self,
                window_surface=pygame.display.set_mode(  # Get a window from the OS
                    size=self.coord_sys.window_size.as_tuple(),
                    flags=pygame.RESIZABLE
                    ))
```

In the above example, I am only writing custom instantiation code for instance
variables that have dependencies on other instance variables. This makes it
easier to see what is going on and how I might decouple things to improve the
code organization.

# Common issues when using a dataclass

## No explicit `__init__()`

Do not write an `__init__()`. Python will let you do it, but you will lose the
benefits of the machine checking you are doing reasonable things. For instance,
you might declare an instance variable listed at the top of the class and then
never use it. If you write an `__init__()`, Python will not stop you from doing
this. If you leave out the `__init__()`, Python will complain that the caller
does not pass the argument for that variable (and then you would catch your
mistake).

## Write `__post_init__()`

If there is code you want to run at instantiation, write a `__post_init__()`.

This is user-defined instantiation code that often involves setting the value
of an instance variable using values that are only known/defined after
`__init__()` has run.

Don't just put `self.blah = blah` in the `__post_init__()`. This is allowed,
but we would like to list all the instance variables at the top of the class,
staying true to the idea that this is like a C struct.

To achieve this, we also import `dataclasses.field` so that we can assign the
instance variable to `field(init=False)` (see
https://docs.python.org/3/library/dataclasses.html#post-init-processing). This
weird syntax is like a placeholder for instance variable definition and, as you
might guess, it tells Python not to include this variable in the `__init__()`.

Without `field(init=False)`, either you would have to assign a dummy value at
the top of the class or the caller would be required to pass a value.

Here is an example using `__post_init__()` and `field(init=False)`:

```python
from dataclasses import dataclass, field
@dataclass
class Art:
    """Container for all artwork to render."""
    shapes: dict[str, list[Line2D]] = field(init=False)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear out all artwork."""
        self.shapes = {"lines": [], "lines_debug": []}
```

Note in the above example, instead of not initializing `shapes` in `__init__()`
we can initialize it with an empty dictionary like this:

```python
    # shapes: dict[str, list[Line2D]] = field(init=False)
    shapes: dict[str, list[Line2D]] = field(default_factory=dict)
```

You might be wondering why we don't just define the initial value of `shapes`
like this:

```python
from dataclasses import dataclass
@dataclass
class Art:
    """Container for all artwork to render."""
    shapes: dict[str, list[Line2D]] = {"lines": [], "lines_debug": []}

    def reset(self) -> None:
        """Clear out all artwork."""
        self.shapes = {"lines": [], "lines_debug": []}
```

Because that throws this error:

```
ValueError: mutable default <class 'dict'> for field shapes is not allowed: use default_factory
```

Here is an example that uses a mix of variables defined in the implicitly
generated `__init__()` (so the caller passes these arguments) and variables
defined in the `__post_init__()`. Note that both types of instance variable are
declared at the top of the class -- we don't have to go digging through all the
code in this class to find all of its instance variables.

```python
@dataclass
class CoordinateSystem:
    panning:        Panning                     # Track panning state
    window_size:    Vec2D                       # Track window size
    gcs_width:      float = 2                   # Initial value GCS -1:1 fills screen width
    pcs_origin:     Point2D = field(init=False) # Game origin in PCS

    def __post_init__(self) -> None:
        self.pcs_origin = self.window_center    # Origin is initially the window center

    @property
    def window_center(self) -> Point2D:
        """The center of the window in pixel coordinates."""
        return Point2D(self.window_size.x/2, self.window_size.y/2)
```

A final common pitfall is to get `AttributeError`:

```python
@dataclass
class Game:
    ...
    entities:   dict[str, Entity] = field(init=False)   # Game characters like the player
    ...
    def __post_init__(self) -> None:
        self.entities["cross"] = Entity()
```

This is missing a crucial piece. We get this error:

```
AttributeError: 'Game' object has no attribute 'entities'
```

I need to create the dict before I can start assigning entries to it:

```python
        self.entities = {}  # <-------------- DON'T FORGET THIS!!!!
        self.entities["cross"] = Entity()
```

## Mutable default values are shared across instances

See https://docs.python.org/3/library/dataclasses.html#mutable-default-values

The following is true for ANY class, not just a dataclass:

Default member variable values are stored in class attributes.

Default member variable values are stored in class attributes.

What? Consider this:

```python
@dataclass
class Entity:
    ...
    origin:             Point2D = Point2D(0, 0)
    ...
```

The above is ALMOST NEVER what you want to do!

Instances of `Entity` will all share the same `origin`: if I update `origin`
for one instance, all instances get the new `origin`. It is a class attribute,
not an instance attribute. Why? Because I gave it a default value.

Note that if the caller explicitly assigns `origin` when instantiating Entity,
`origin` *will* be distinct!

```python
        self.entities = {}
        self.entities["player"] = Entity(
                origin=Point2D(0, 0),
                )
        self.entities["cross"] = Entity(
                origin=Point2D(0, 0),
                )
```

But that is not a good fix. It is a trap for the user. In fact, this behavior is also a trap to the lib developer: if you only ever exercise the lib code by instantiating with values for `origin`, you would never catch that `origin` is (otherwise) going to behave like a class variable!

One way to avoid this is to to say we don't want the user to assign a value by
using `field(init=False)`, and then we assign it in the `__post_init__()`:


```python
@dataclass
class Entity:
    ...
    origin:             Point2D = field(init=False)
    ...

    def __post_init__(self) -> None:
        self.origin = Point2D(0, 0)
```

But this prevents the caller from providing `origin`. So this should only be
used for values we specifically want the lib code to calculate.

The solution you want to use most of the time is a `default_factory` and define
a `lambda` that says what to use as the default.

```python
@dataclass
class Entity:
    ...
    origin:             Point2D = field(default_factory=lambda: Point2D(0, 0))
    ...
```

This is saying, "hey, if no default value is given, here is a function (the
`lambda`) you can call. The function is simple, it just calls `Point2D(0, 0)`.
This forces us to get an instance attribute rather than a class attribute for
`origin`.

To recap: the moment you instantiate a class more than once, you may find that
some instance variables are actually class variables because your instances
seem to share values. In this regard, the above two fixes are equivalent (`__post_init__()` vs `default_factory`).

The `default_factory` style makes it a single line:

```
    amount_excited:     AmountExcited = field(default_factory=lambda: AmountExcited())
    origin:             Point2D = field(default_factory=lambda: Point2D(0, 0))
```

And `default_factory` has the added benefit that the caller can still provide
this argument if they so choose.

The `__post_init__` style setting `field(init=False)` prevents the caller from
providing this argument. Reserve initializing members in `__post_init__` for
the members that are calculated by the library.

## Printing classes

Use the `__str__()` method for custom printing. This is helpful for debugging.
Don't define a `__repr__()` method -- let the `@dataclass` decorator do that
for you (the `__repr__()` method is supposed to be formatted in a way that is
executable code).

For example, with no `__str__()` defined, printing `TickCounter` uses its `__repr__()`:

```
TickCounter(ticks=..., period=3, count=0, name='bob')
```

I want a more concise format for printing a `TickCounter` in the Debug HUD:

```python
@dataclass
class TickCounter:
    ...
    def __str__(self) -> str:
        return f"{self.name}({self.period} frames): {self.count}"
```

The above format tells me the name of the `TickCounter`, the number of frames
in one period, and the count of periods thus far. For example, printing an
instance of `TickCounter` results in something like this:

```
bob(3 frames): 123
```

### Printing classes that use other classes

Say class `Ticks` has an attribute that is an instance of class `TickCounter`.
If I print an instance of `Ticks`, I get the `__repr__()` of `TickCounter`, not its `__str__()`.

To get the `__str__()`, I have to explicitly print the class attribute that is
the instance of `TickCounter`.

### Pretty print a matrix

```python
FLOAT_ROUND_NDIGITS = 14
FLOAT_PRINT_WIDTH = FLOAT_ROUND_NDIGITS + 3  # Account for "0." and one space

@dataclass
class Matrix2D:
    ...
    def __str__(self) -> str:
        w = FLOAT_PRINT_WIDTH  # Right-align each entry to be this wide
        m11 = round(self.m11, FLOAT_ROUND_NDIGITS)
        m12 = round(self.m12, FLOAT_ROUND_NDIGITS)
        m21 = round(self.m21, FLOAT_ROUND_NDIGITS)
        m22 = round(self.m22, FLOAT_ROUND_NDIGITS)
        return (f"|{m11:>{w}} {m12:>{w}}|\n"
                f"|{m21:>{w}} {m22:>{w}}|")
```

### Precision when printing types with floats

`Point2D` has float attributes `x` and `y`.

I use a default precision for floats in `__str__()`, but offer another `fmt()`
method that requires explicitly stating the precision:

```python
FLOAT_PRINT_PRECISION = 0.2

@dataclass
class Point2D:
    ...
    def __str__(self) -> str:
        """Point as string with two decimal places (default: FLOAT_PRINT_PRECISION)."""
        return self.fmt(FLOAT_PRINT_PRECISION)

    def fmt(self, precision: float) -> str:
        """Point as a string with the desired precision."""
        return f"({self.x:{precision}f}, {self.y:{precision}f})"
```
