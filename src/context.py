#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Share global game state."""


class Context:
    """Global context."""
    game: "Game" = None
    renderer: "Renderer" = None

    @classmethod
    def register_game(cls, instance: "Game") -> None:
        """Load global handle to the instance of game"""
        cls.game = instance

    @classmethod
    def register_renderer(cls, instance: "Renderer") -> None:
        """Load global handle to the instance of renderer"""
        cls.renderer = instance
