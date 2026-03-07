#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Share global game state."""


class Context:
    """Global context."""
    game: "Game" = None
    renderer: "Renderer" = None
    timing: "Timing" = None

    @classmethod
    def register_game(cls, instance: "Game") -> None:
        """Load global handle to the instance of Game"""
        cls.game = instance

    @classmethod
    def register_renderer(cls, instance: "Renderer") -> None:
        """Load global handle to the instance of Renderer"""
        cls.renderer = instance

    @classmethod
    def register_timing(cls, instance: "Timing") -> None:
        """Load global handle to the instance of Timing"""
        cls.timing = instance
