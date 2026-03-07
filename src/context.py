#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Share global game state."""

# LEFTOFF: document this: instead of a global var, we make a class to namespace


# pylint: disable=too-few-public-methods
class Context:
    """Global context."""
    game: "Game" = None

    @classmethod
    def register_game(cls, instance: "Game") -> None:
        """Load global handle to the instance of game"""
        cls.game = instance
