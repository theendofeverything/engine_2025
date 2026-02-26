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
