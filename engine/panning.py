#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Panning.
"""

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
