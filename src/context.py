#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Share global game state."""

import inspect
from typing import Type, TypeVar, Any
T = TypeVar("T")


def namespace(cls: Type[T]) -> Type[T]:
    """Class decorator to identify a Namespace Class (a class that cannot be instantiated).

    A Namespace Class is a class you never instantiate. It is simply for grouping data and functions
    together.

    Adding this decorator to a class overrides its `__init__()` method with a function that throws a
    RuntimeError if instantiation is attempted.

    Adding this decorator also provides the convenience function `state_str()` for printing the
    public class members.
    """

    def no_init(self: Any) -> None:
        """Prevent instantiation"""
        raise RuntimeError(f"{cls.__name__} is a Namespace Class and cannot be instantiated.")

    def state_str() -> str:
        """Return pretty string of public class members.

        Members omitted from this string:
        - beginning with an underscore
        - any methods, including classmethods and staticmethods
        """
        attrs = {
            k: v for k, v in cls.__dict__.items()
            if not k.startswith("_")
            and not inspect.isroutine(v)
            and not isinstance(v, (classmethod, staticmethod))
        }
        items = [f"{k}={v!r}" for k, v in attrs.items()]
        return f"{cls.__name__}({', '.join(items)})"

    setattr(cls, "__init__", no_init)
    setattr(cls, "state_str", state_str)
    return cls


# NOT USED -- replaced by @namespace decorator
def namespace_class_str(cls: "Class") -> str:
    """Return pretty string of public class members."""
    attrs = {
            k: v for k, v in cls.__dict__.items()
            if not k.startswith("_")
            }
    items = [f"{k}={v!r}" for k, v in attrs.items()]
    return f"{cls.__name__}({', '.join(items)})"


@namespace
class Context:
    """Global context.

    Context is populated when `Game.setup()` is called.
    >>> from .game import Game
    >>> _ = Game.setup()

    Context is a mix of Namespace Classes like 'Game' and Global Singletons like `Renderer`:
    >>> print(Context.state_str())
    Context(game=<class 'src.game.Game'>,
        renderer=Renderer(...),
        timing=Timing(...))

    Modules access global context like this:
    >>> Context.game.debug_font
    'fonts/ProggyClean.ttf'
    """
    game: "Game" = None
    renderer: "Renderer" = None
    timing: "Timing" = None

    @classmethod
    def register_game(cls, game_class: Type[T]) -> None:
        """Load global handle to the instance of Game"""
        cls.game = game_class

    @classmethod
    def register_renderer(cls, instance: "Renderer") -> None:
        """Load global handle to the instance of Renderer"""
        cls.renderer = instance

    @classmethod
    def register_timing(cls, instance: "Timing") -> None:
        """Load global handle to the instance of Timing"""
        cls.timing = instance
