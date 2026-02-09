# `classmethod`

A `classmethod` is a method is an alternate way of constructing an instance. Example:

```python
@dataclass
class Point2D:
    x: float
    y: float

    ...
    @classmethod
    def from_tuple(cls, position: tuple[float, float]) -> Point2D:
        """Create a point from a pygame event position (x, y)."""
        return cls(x=position[0], y=position[1])
```

A `Point2D` is instantiated with `Point2D(x=1,y=2)` or, using the `classmethod`
with `Point2D(position)` where `position=(1,2)`.

# `staticmethod`

A `staticmethod` is a function that logically belongs with a class but does
  not use any data from an instance of the class. For example:


```python
@dataclass
class CoordinateSystem:

    @staticmethod
    def xfm(v: Vec2D, mat: Matrix2DH) -> Vec2D:
        return mat.multiply_vec(v)
```

The math to do a coordinate system transform logically belongs with the
CoordinateSystem class. The CoordinateSystem class provides all the coordinate
systems used in the game by constructing them from global game data.

The caller has to specify the transformation matrix because there are multiple
matrices to choose from. And the caller has to specify the vector to be
transformed. The transform does not need any other information, so this does
not need to be an instance method. It is a static method because it does not
access any attributes because the caller has to pass everything in.

# `classmethod` with `Enum`

Consider this `Enum` of the five values of `event.button`:
```python
class MouseButton(Enum):
    """Enumerate the mouse button values from pygame.Event.button"""
    UNKNOWN = 0
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEELUP = 4
    WHEELDOWN = 5
```

The naive way to use this `Enum` to convert an `event.button` to a `MouseButton` is with a `match` statement:

```python
match event.button:
    case 1:
        mouse_button = MouseButton.LEFT
    case 2:
        mouse_button = MouseButton.MIDDLE
    case 2:
        mouse_button = MouseButton.RIGHT
    case 4:
        mouse_button = MouseButton.WHEELUP
    case 5:
        mouse_button = MouseButton.WHEELDOWN
    case _:
        mouse_button = MouseButton.UNKNOWN
```

Here is a better way using a `classmethod` (and it eliminates the need for the `UNKNOWN` button value):

```python
class MouseButton(Enum):
    """Enumerate the mouse button values from pygame.Event.button"""
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEELUP = 4
    WHEELDOWN = 5

    @classmethod
    def from_event(cls, event: pygame.Event) -> MouseButton:
        """Get MouseButton from event.button."""
        return cls(event.button)
```

Now I can get the `MouseButton.LEFT`, `MouseButton.MIDDLE`, etc., from an
`event.button` by simply calling `from_event()`:

```python
MouseButton.from_event(event)
```
