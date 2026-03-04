# How to use a Class to group data and methods

## The beginner way is often not what you want

The first way beginners learn to define Classes in Python is with the
boilerplate `__init__()`:

```python
class Vector:
    """The usual way to make a class for instantiation has the boilerplate __init__()."""
    def __init__(self) -> None:
        self.components = [1, 2]
```

We have to instantiate `Vector` to access attribute `components`:

```python
    >>> Vector().components
    [1, 2]
```

And we need to store that instance somewhere if we want to access it again:

```python
    >>> vec = Vector()
    >>> vec.components
    [1, 2]
```

## Just use a Class if you can

I often do not need to create an instance. I just need to store global data and
to group functions with that data. 

Python supports this style of programming.

**Python supports this style of programming.**

Just create a Class:

- Create class variables as you normally would.
- Create class methods to update the class variable.

Consider our simple class again, but now with no intention of being instantiated:

```python
class Vector:
    components: list[int | float] = [1, 2]  # <--- This is a class variable.
```

We can directly access `components` without making an instance variable. And we
can see that the value of the class variable is retained.

```python
    >>> components = [1, 2, 4]
    >>> Vector.components = components
    >>> Vector.components
    [1, 2, 4]
```

**We have a Global Singleton.**

## Use a dataclass if you need to make instances

Now let's add the `@dataclass` decorator to turn this back into a class that we can instantiate, but without all of the boilerplate:

```python
@dataclass
class Vector:
    components: list[int | float] = [1, 2]  # <--- This is a class variable.
```

The first problem we run into is a `ValueError`:

```
ValueError: mutable default <class 'list'> for field components is not allowed: use default_factory
```

We can fix this by eliminating the default value:

```python
    components: list[int | float]
```

Or if we want the default, we can use `field(default_factory=...)`:

```python
from dataclasses import dataclass, field
    ...
    components: list[int | float] = field(default_factory=lambda: [1, 2])
```

Note: If we needed to calculate the default value, we would use a `__post_init__()`:

```python
    components: list[int | float] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.components = [1, 2]  # These values would be calculated
```

The next problem is that we can no longer access `components` with this syntax:

```python
    >>> Vector.components
```

Python sees `Vector` only as a type, and the type does not have attribute `components`:

```
    AttributeError: type object 'Vector' has no attribute 'components'
```

Instead we have to create an instance:

```python
    >>> Vector().components
```

## Class vs Dataclass

Notice how similar the syntax of a `class` definition is for the class with
`@dataclass` decorator and the `class` used as a global singleton.

My guess is that `@dataclass` arose out of people using the simpler global
singleton `class` syntax but then wanting a way to maintain that syntax while
still being able to create multiple instances with independent state.

I learned about `@dataclass` before I learned I can use `class` as a global
singleton. I am realizing that many of the places I was using `@dataclasss`
should simply be a `class` with `@classmethod` methods.

# Methods

There is a little more to it, so here are some examples.

## Toy Example of a Global Singleton

```python
class Vector:
    """Class as a global singleton.

    A Class can store data grouped with methods WITHOUT creating an instance!

    The class has some initial data in it:
    >>> Vector.components
    [1, 2]

    We can call the classes methods directly on that data:
    >>> Vector.sum()
    3

    Those methods can modify the data:
    >>> Vector.append(3.0)
    >>> Vector.components
    [1, 2, 3.0]
    >>> Vector.sum()
    6.0
    """
    components: list[int | float] = [1, 2]  # <--- This is a class variable.

    @classmethod
    def append(cls, component: int | float) -> None:
        """Update my components."""
        cls.components.append(component)

    @classmethod
    def sum(cls) -> int | float:
        """Return the sum of my components."""
        _sum: int | float = 0
        for n in cls.components:
            _sum += n
        return _sum
```

## Toy Example of a Dataclass with classmethod

```python
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class AltVector:
    """Class for making instances.

    Turn this into a class that makes instances with the 'dataclass' decorator:

    1. Note that the syntax to define attribute 'components' is exactly the same!

    2. But classmethod sum() must turn into an instance method (no 'classmethod'
       decorator). Since this is a 'dataclass', the 'classmethod' decorator will
       treat the first argument as the class type, which does not have any
       attributes or methods, it is just a data type.

       When we remove the 'classmethod' decorator, the first argument refers to
       an instance, not the class. We could leave the argument name "cls" (the
       Python runtime doesn't care) but that would be confusing. Call it "self".

    3. The use of 'classmethod' in a 'dataclass' is to make a new constructor.
       from_list() is an example: it makes an instances from a list (this could
       be some other datatype that makes sense) instead of having to use the
       type of attribute 'components' (which also happens to be a list in this
       case).

    >>> vec = AltVector.from_list([1.0,2.0])
    >>> vec
    AltVector(components=[1.0, 2.0])
    >>> vec.sum()
    3.0
    """
    components: list[int | float]  # <--- This is an instance variable.

    def sum(self) -> int | float:
        """Return the sum of my components."""
        _sum: int | float = 0
        for n in self.components:
            _sum += n
        return _sum

    @classmethod
    def from_list(cls, components: list[int | float]) -> AltVector:
        """Return a Vector made from a list."""
        return cls(components)
```

# And here are actual examples from code

## Example 1 - Mouse as a Global Singleton

```python
class Mouse:
    """Track mouse state in a Global Singleton.

    Button state begins with no buttons pressed:
    >>> Mouse.is_pressed(MouseButton.LEFT)
    False

    Simulate a left-click:
    >>> event = pygame.Event(pygame.MOUSEBUTTONDOWN, {'button': 1})

    Update the button state:
    >>> Mouse.update(event)

    Check that we have updated the state of the left mouse button:
    >>> Mouse.is_pressed(MouseButton.LEFT)
    True

    Convert pygame.Event.button 'int' type to a MouseButton Enum:
    >>> mouse_button = MouseButton.from_event(event)

    Print the button state (TRUE) using its name (LEFT) instead of its value (1):
    >>> print(f"Mouse.is_pressed({mouse_button.name}): {Mouse.is_pressed(mouse_button)}")
    Mouse.is_pressed(LEFT): True

    Note the use of 'MouseButton' vs 'MouseButton.name':
        - 'MouseButton' gets the 'int' value (1, 2, etc.)
        - 'MouseButton.name' gets the button name ('LEFT', 'MIDDLE', etc.)
    """
    # Store states for all 5 buttons: Pressed (True) and NotPressed (False)
    _state = {button.value: False for button in MouseButton}

    @classmethod
    def update(cls, event: pygame.Event) -> None:
        """Update the state of all buttons in MouseButton."""
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                cls._state[event.button] = True
            case pygame.MOUSEBUTTONUP:
                cls._state[event.button] = False

    @classmethod
    def is_pressed(cls, button: MouseButton) -> bool:
        """Return True/False if button MouseButton is pressed.

        If the "button" does not exist, return False instead of None:
        >>> Mouse.is_pressed(6)
        False
        """
        return cls._state.get(button, False)
```

## Example 2 - Art

### original version

```python
@dataclass
class Art:
    """Container for all artwork to render."""
    lines: list[Line2D] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear out all artwork."""
        self.lines = []

    def randomize_line(self, line: Line2D, wiggle: float = 0.01) -> Line2D:
        """Randomize the start and end points of the line by 'wiggle'.

        wiggle (float):
            A value between 0 and 0.1
        """
        return Line2D(start=Point2D(
                          line.start.x + random.uniform(-1*wiggle, wiggle),
                          line.start.y + random.uniform(-1*wiggle, wiggle)
                          ),
                      end=Point2D(
                          line.end.x + random.uniform(-1*wiggle, wiggle),
                          line.end.y + random.uniform(-1*wiggle, wiggle)
                          ),
                      color=line.color
                      )

    def draw_lines(self, points: list[Point2D], color: Color) -> None:
        """Draw lines given a list of points."""
        # Draw lines between pairs of points
        for i in range(len(points)-1):
            self.lines.append(Line2D(points[i], points[i+1], color))
        # Draw line from last point back to first point
        self.lines.append(Line2D(points[-1], points[0], color))
```

### As a Global Singleton

```python
class Art:
    """Container for all artwork to render."""
    lines: list[Line2D] = []

    @classmethod
    def reset(cls) -> None:
        """Clear out all artwork."""
        cls.lines = []

    @staticmethod
    def randomize_line(line: Line2D, wiggle: float = 0.01) -> Line2D:
        """Randomize the start and end points of the line by 'wiggle'.

        wiggle (float):
            A value between 0 and 0.1
        """
        return Line2D(start=Point2D(
                          line.start.x + random.uniform(-1*wiggle, wiggle),
                          line.start.y + random.uniform(-1*wiggle, wiggle)
                          ),
                      end=Point2D(
                          line.end.x + random.uniform(-1*wiggle, wiggle),
                          line.end.y + random.uniform(-1*wiggle, wiggle)
                          ),
                      color=line.color
                      )

    @classmethod
    def draw_lines(cls, points: list[Point2D], color: Color) -> None:
        """Draw lines given a list of points."""
        # Draw lines between pairs of points
        for i in range(len(points)-1):
            cls.lines.append(Line2D(points[i], points[i+1], color))
        # Draw line from last point back to first point
        cls.lines.append(Line2D(points[-1], points[0], color))
```

## Example 3 - Panning

### original version

```python
@dataclass
class Panning:
    """Track mouse panning state.

    >>> panning = Panning()                             # Track panning state
    >>> mouse_pos = (123, 456)                          # Position when button 1 was pressed
    >>> panning.begin = Point2D.from_tuple(mouse_pos)   # Track panning begin position
    >>> mouse_pos = (246, 456)                          # Position later while still panning
    >>> panning.end = Point2D.from_tuple(mouse_pos)     # Track latest panning position
    >>> panning.vector                                  # Report the latest panning vector
    Vec2D(x=123, y=0)
    """
    begin:                  Point2D = field(init=False)
    end:                    Point2D = Point2D(0, 0)     # Dummy initial value
    is_active:              bool = False

    def __post_init__(self) -> None:
        self.begin = self.end                           # Zero-out the panning vector

    @property
    def vector(self) -> Vec2D:
        """Return the panning vector: describes amount of mouse pan."""
        return Vec2D.from_points(start=self.begin, end=self.end)

    def start(self, position: tuple[int | float, int | float]) -> None:
        """User started panning."""
        panning = self
        panning.is_active = True
        panning.begin = Point2D.from_tuple(position)

    def stop(self, game: "Game") -> None:
        """User stopped panning."""
        panning = self
        panning.is_active = False
        game.coord_sys.pcs_origin = game.coord_sys.translation.as_point()  # Set new origin
        panning.begin = panning.end  # Zero-out the panning vector

    def update(self) -> None:
        """Update 'panning.end': the latest point the mouse has panned to.

        Dependency chain depicting how panning manifests as translating the game
        view on the screen:
            renderer <-- coord_sys.matrix.gcs_to_pcs <-- coord_sys.translation <-- panning.vector

            In the above dependency chain:
                - read "<--" as "thing-on-left uses thing-on-right"
                - panning.vector = panning.end - panning.begin
        """
        panning = self
        if panning.is_active:
            mouse_pos = pygame.mouse.get_pos()
            panning.end = Point2D.from_tuple(mouse_pos)
```

As a global instance, `Panning()` had to live somewhere, so I had it in
`OngoingAction`. But this was a bit arbitrary. It's cleaner to just let anyone access the Global Singleton by importing `Panning` from `gamelibs.input_mapper`.

Here is `Panning()` in `OngoingAction`:

```python
class OngoingAction:
    """Actions that last for multiple frames such as click-drag."""

    panning: Panning = Panning()
    drag_player_is_active: bool = False

    def update(self, game: "Game") -> None:
        """Update all ongoing actions."""
        ongoing_action = self
        ongoing_action.panning.update()
        ongoing_action.drag_player(game)
```

### As a Global Singleton

```python
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
    def stop(cls, game: "Game") -> None:
        """User stopped panning."""
        panning = cls
        panning.is_active = False
        game.coord_sys.pcs_origin = game.coord_sys.translation.as_point()  # Set new origin
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

And here is `OngoingAction` without owning the `Panning()` global instance, but
still responsible for updating the `Panning` state when ongoing actions are
updated by `Game`:

```python
class OngoingAction:
    """Actions that last for multiple frames such as click-drag."""

    drag_player_is_active: bool = False

    def update(self, game: "Game") -> None:
        """Update all ongoing actions."""
        ongoing_action = self
        Panning.update()
        ongoing_action.drag_player(game)
```

In the `Game` code, we used to have a line like this:

```python
                game.input_mapper.ongoing_action.panning.start(position)
```

That becomes this:

```python
                Panning.start(position)
```

When we debug `Panning`, we can simply `from .input_mapper import Panning` and
look at `Panning.begin` and `Panning.end`. We don't need to go through
`InputMapper` or through `Game`.

```python
from .input_mapper import Panning
...
@dataclass
class DebugGame:
    ...
    def panning(self, show_in_hud: bool) -> None:
        ...
        debug.hud.print(f"|\n+- Panning (Ctrl+Left-Click-Drag): {Panning.is_active} ({FILE})")
        debug.hud.print(f"|        +- .begin: {Panning.begin.fmt(0.0)}")
        debug.hud.print(f"|        +- .end: {Panning.end.fmt(0.0)}")
        debug.hud.print(f"|        +- .vector: {Panning.vector().fmt(0.0)}")
        ...
```

## Example 4 - InputMapper

### original version

There is only one InputMapper. So why make this a dataclass?

```python
pylint: disable=line-too-long
@dataclass
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod, keydirection): Action}
    mouse_map: {(mousebutton, keymod, buttondirection): Action}

    >>> input_mapper = InputMapper()
    >>> key_map = input_mapper.key_map
    >>> key_map
    {(99, <KeyModifier.NO_MODIFIER: 0>, <KeyDirection.DOWN: 2>): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
    (100, <KeyModifier.NO_MODIFIER: 0>, <KeyDirection.DOWN: 2>): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,
    (98, <KeyModifier.SHIFT: 3>, <KeyDirection.DOWN: 2>): <Action.CONTROLS_ADJUST_B_LESS: 11>,
    ...

    >>> mouse_map = input_mapper.mouse_map
    >>> mouse_map
    {(<MouseButton.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<MouseButton.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<MouseButton.MIDDLE: 2>, <KeyModifier.NO_MODIFIER: 0>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<MouseButton.MIDDLE: 2>, <KeyModifier.NO_MODIFIER: 0>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<MouseButton.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.DOWN: 2>): <Action.START_DRAG_PLAYER: 26>,
    (<MouseButton.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.UP: 1>): <Action.STOP_DRAG_PLAYER: 27>}
    """
    ongoing_action: OngoingAction = OngoingAction()
    key_map: dict[tuple[int,  # event.key
                        KeyModifier,  # enum wrapper on pygame kmod
                        KeyDirection  # enum -- UP or DOWN
                        ],
                  Action  # enum
                  ] = field(default_factory=dict)
    mouse_map: dict[tuple[MouseButton,  # enum wrapper on pygame event.button int
                          KeyModifier,  # enum wrapper on pygame kmod
                          ButtonDirection  # enum -- UP or DOWN
                          ],
                    Action  # enum
                    ] = field(default_factory=dict)

    # pylint: disable=line-too-long
    def __post_init__(self) -> None:
        self.mouse_map = {
            (MouseButton.LEFT,   KeyModifier.PANNING,     ButtonDirection.DOWN): Action.START_PANNING,
            (MouseButton.LEFT,   KeyModifier.PANNING,     ButtonDirection.UP):   Action.STOP_PANNING,
            (MouseButton.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.DOWN): Action.START_PANNING,
            (MouseButton.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.UP):   Action.STOP_PANNING,
            (MouseButton.LEFT,   KeyModifier.SHIFT,    ButtonDirection.DOWN):    Action.START_DRAG_PLAYER,
            (MouseButton.LEFT,   KeyModifier.SHIFT,    ButtonDirection.UP):      Action.STOP_DRAG_PLAYER,
            }

        self.key_map = {
            (pygame.K_c,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK,
            (pygame.K_d,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_DEBUG_ART_OVERLAY,
            (pygame.K_b,      KeyModifier.SHIFT,       KeyDirection.DOWN):   Action.CONTROLS_ADJUST_B_LESS,
            (pygame.K_b,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_ADJUST_B_MORE,
            (pygame.K_k,      KeyModifier.SHIFT,       KeyDirection.DOWN):   Action.CONTROLS_ADJUST_K_LESS,
            (pygame.K_k,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_ADJUST_K_MORE,
            (pygame.K_1,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_PICK_MODE_1,
            (pygame.K_2,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_PICK_MODE_2,
            (pygame.K_3,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_PICK_MODE_3,
            (pygame.K_q,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.QUIT,
            (pygame.K_SPACE,  KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_PAUSE,
            (pygame.K_F11,    KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_FULLSCREEN,
            (pygame.K_F12,    KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_DEBUG_HUD,
            (pygame.K_EQUALS, KeyModifier.SHIFT_CTRL,  KeyDirection.DOWN):   Action.FONT_SIZE_INCREASE,
            (pygame.K_MINUS,  KeyModifier.CTRL,        KeyDirection.DOWN):   Action.FONT_SIZE_DECREASE,
            (pygame.K_LEFT,   KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_LEFT_GO,
            (pygame.K_RIGHT,  KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_RIGHT_GO,
            (pygame.K_UP,     KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_UP_GO,
            (pygame.K_DOWN,   KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_DOWN_GO,
            (pygame.K_LEFT,   KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_LEFT_STOP,
            (pygame.K_RIGHT,  KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_RIGHT_STOP,
            (pygame.K_UP,     KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_UP_STOP,
            (pygame.K_DOWN,   KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_DOWN_STOP,
            (pygame.K_RCTRL,  KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_PANNING,
            (pygame.K_LCTRL,  KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_PANNING,
            (pygame.K_RSHIFT, KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_DRAG_PLAYER,
            (pygame.K_LSHIFT, KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_DRAG_PLAYER,
            }

    def action_for_key_event(
            self,
            log: logging.Logger,
            event: pygame.event.Event,
            kmod: int
            ) -> Action | None:
        """Return the Action (enum) matching this key event."""
        input_mapper = self
        match event.type:
            case pygame.KEYDOWN: key_direction = KeyDirection.DOWN
            case pygame.KEYUP: key_direction = KeyDirection.UP
            case _: sys.exit()  # Should never happen!
        log.debug(f"{key_direction}: {pygame.key.name(event.key)}")
        action = input_mapper.key_map.get(
                (event.key,
                 KeyModifier.from_kmod(kmod),
                 key_direction)
                )
        log.debug(f"action: {action}")
        return action

    def action_for_mouse_button_event(
            self,
            log: logging.Logger,
            event: pygame.event.Event,
            kmod: int
            ) -> Action | None:
        """Return the Action (enum) matching this mouse button event."""
        input_mapper = self
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                button_direction = ButtonDirection.DOWN
                Mouse.update(event)
            case pygame.MOUSEBUTTONUP:
                button_direction = ButtonDirection.UP
                Mouse.update(event)
            case _: sys.exit()  # Should never happen!
        mouse_button = MouseButton.from_event(event)
        log.debug(f"Event MOUSEBUTTON {button_direction}, "
                  f"pos: {event.pos}, ({type(event.pos[0])}), "
                  f"event.button: {event.button}, "
                  f"Mouse.is_pressed({mouse_button.name}): {Mouse.is_pressed(mouse_button)}")
        action = input_mapper.mouse_map.get(
                (mouse_button,
                 KeyModifier.from_kmod(kmod),
                 button_direction)
                )
        log.debug(f"action: {action}")
        return action
```

### As a Global Singleton

The `class`-only version of `InputMapper` is almost exactly the same as the
`dataclass` version (not a surprise).

The real difference is in how `InputMapper` is used by `Game`:

- no need to instantiate an `input_mapper = InputMapper()` attribute
- instead of `self.input_mapper` whatever, we just do `InputMapper` whatever

This is a bigger win that it might seem. `CoordinateSystem` needed access to
`Game.input_mapper` to access the instance of `Panning`, so we had this in the
`Game` `__post_init__()`:

```python
    def __post_init__(self) -> None:
        self.coord_sys = CoordinateSystem(
                window_size=Vec2D.from_tuple(self.renderer.window.size),
                panning=self.input_mapper.ongoing_action.panning)
                )
```

By making `InputMapper` a global singleton class, we can get rid of this. In
fact, I go even further and make `Panning` a global singleton class so that
`CoordinateSystem` directly depends on `Panning`. Either way, now the
`__post_init__()` definition of `Game.coord_sys` just needs the window size:

```python
    def __post_init__(self) -> None:
        self.coord_sys = CoordinateSystem(
                window_size=Vec2D.from_tuple(self.renderer.window.size)
                )
```

Here is an example showing how `self.input_mapper` whatever becomes just
`InputMapper`:

```python
    def loop(self, log: logging.Logger) -> None:
        ...
        InputMapper.ongoing_action.update(self)
        ...

    def do_action_for_mouse_button_event(self, action: Action, position: tuple[int, int]) -> None:
        match action:
            ...
            case Action.START_DRAG_PLAYER:
                InputMapper.ongoing_action.drag_player_is_active = True
            case Action.STOP_DRAG_PLAYER:
                InputMapper.ongoing_action.drag_player_is_active = False
```

Here is the new `InputMapper` definition, again this is very similar to the
`dataclass` version:

```python
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod, keydirection): Action}
    mouse_map: {(mousebutton, keymod, buttondirection): Action}

    >>> InputMapper.key_map
    {(99, <KeyModifier.NO_MODIFIER: 0>, <KeyDirection.DOWN: 2>): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
    (100, <KeyModifier.NO_MODIFIER: 0>, <KeyDirection.DOWN: 2>): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,
    (98, <KeyModifier.SHIFT: 3>, <KeyDirection.DOWN: 2>): <Action.CONTROLS_ADJUST_B_LESS: 11>,
    ...

    >>> InputMapper.mouse_map
    {(<MouseButton.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<MouseButton.LEFT: 1>, <KeyModifier.CTRL: 192>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<MouseButton.MIDDLE: 2>, <KeyModifier.NO_MODIFIER: 0>, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>,
    (<MouseButton.MIDDLE: 2>, <KeyModifier.NO_MODIFIER: 0>, <ButtonDirection.UP: 1>): <Action.STOP_PANNING: 25>,
    (<MouseButton.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.DOWN: 2>): <Action.START_DRAG_PLAYER: 26>,
    (<MouseButton.LEFT: 1>, <KeyModifier.SHIFT: 3>, <ButtonDirection.UP: 1>): <Action.STOP_DRAG_PLAYER: 27>}
    """
    ongoing_action: OngoingAction = OngoingAction()
    key_map: dict[tuple[int,  # event.key
                        KeyModifier,  # enum wrapper on pygame kmod
                        KeyDirection  # enum -- UP or DOWN
                        ],
                  Action  # enum
                  ] = {
            (pygame.K_c,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK,
            (pygame.K_d,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_DEBUG_ART_OVERLAY,
            (pygame.K_b,      KeyModifier.SHIFT,       KeyDirection.DOWN):   Action.CONTROLS_ADJUST_B_LESS,
            (pygame.K_b,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_ADJUST_B_MORE,
            (pygame.K_k,      KeyModifier.SHIFT,       KeyDirection.DOWN):   Action.CONTROLS_ADJUST_K_LESS,
            (pygame.K_k,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_ADJUST_K_MORE,
            (pygame.K_1,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_PICK_MODE_1,
            (pygame.K_2,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_PICK_MODE_2,
            (pygame.K_3,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.CONTROLS_PICK_MODE_3,
            (pygame.K_q,      KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.QUIT,
            (pygame.K_SPACE,  KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_PAUSE,
            (pygame.K_F11,    KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_FULLSCREEN,
            (pygame.K_F12,    KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.TOGGLE_DEBUG_HUD,
            (pygame.K_EQUALS, KeyModifier.SHIFT_CTRL,  KeyDirection.DOWN):   Action.FONT_SIZE_INCREASE,
            (pygame.K_MINUS,  KeyModifier.CTRL,        KeyDirection.DOWN):   Action.FONT_SIZE_DECREASE,
            (pygame.K_LEFT,   KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_LEFT_GO,
            (pygame.K_RIGHT,  KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_RIGHT_GO,
            (pygame.K_UP,     KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_UP_GO,
            (pygame.K_DOWN,   KeyModifier.NO_MODIFIER, KeyDirection.DOWN):   Action.PLAYER_MOVE_DOWN_GO,
            (pygame.K_LEFT,   KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_LEFT_STOP,
            (pygame.K_RIGHT,  KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_RIGHT_STOP,
            (pygame.K_UP,     KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_UP_STOP,
            (pygame.K_DOWN,   KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.PLAYER_MOVE_DOWN_STOP,
            (pygame.K_RCTRL,  KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_PANNING,
            (pygame.K_LCTRL,  KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_PANNING,
            (pygame.K_RSHIFT, KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_DRAG_PLAYER,
            (pygame.K_LSHIFT, KeyModifier.NO_MODIFIER, KeyDirection.UP):     Action.STOP_DRAG_PLAYER,
            }
    # pylint: disable=line-too-long
    mouse_map: dict[tuple[MouseButton,  # enum wrapper on pygame event.button int
                          KeyModifier,  # enum wrapper on pygame kmod
                          ButtonDirection  # enum -- UP or DOWN
                          ],
                    Action  # enum
                    ] = {
            (MouseButton.LEFT,   KeyModifier.PANNING,     ButtonDirection.DOWN): Action.START_PANNING,
            (MouseButton.LEFT,   KeyModifier.PANNING,     ButtonDirection.UP):   Action.STOP_PANNING,
            (MouseButton.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.DOWN): Action.START_PANNING,
            (MouseButton.MIDDLE, KeyModifier.NO_MODIFIER, ButtonDirection.UP):   Action.STOP_PANNING,
            (MouseButton.LEFT,   KeyModifier.SHIFT,    ButtonDirection.DOWN):    Action.START_DRAG_PLAYER,
            (MouseButton.LEFT,   KeyModifier.SHIFT,    ButtonDirection.UP):      Action.STOP_DRAG_PLAYER,
            }

    @classmethod
    def action_for_key_event(
            cls,
            log: logging.Logger,
            event: pygame.event.Event,
            kmod: int
            ) -> Action | None:
        """Return the Action (enum) matching this key event."""
        match event.type:
            case pygame.KEYDOWN: key_direction = KeyDirection.DOWN
            case pygame.KEYUP: key_direction = KeyDirection.UP
            case _: sys.exit()  # Should never happen!
        log.debug(f"{key_direction}: {pygame.key.name(event.key)}")
        action = cls.key_map.get(
                (event.key,
                 KeyModifier.from_kmod(kmod),
                 key_direction)
                )
        log.debug(f"action: {action}")
        return action

    @classmethod
    def action_for_mouse_button_event(
            cls,
            log: logging.Logger,
            event: pygame.event.Event,
            kmod: int
            ) -> Action | None:
        """Return the Action (enum) matching this mouse button event."""
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                button_direction = ButtonDirection.DOWN
                Mouse.update(event)
            case pygame.MOUSEBUTTONUP:
                button_direction = ButtonDirection.UP
                Mouse.update(event)
            case _: sys.exit()  # Should never happen!
        mouse_button = MouseButton.from_event(event)
        log.debug(f"Event MOUSEBUTTON {button_direction}, "
                  f"pos: {event.pos}, ({type(event.pos[0])}), "
                  f"event.button: {event.button}, "
                  f"Mouse.is_pressed({mouse_button.name}): {Mouse.is_pressed(mouse_button)}")
        action = cls.mouse_map.get(
                (mouse_button,
                 KeyModifier.from_kmod(kmod),
                 button_direction)
                )
        log.debug(f"action: {action}")
        return action
```
