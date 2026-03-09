#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Ongoing Actions are user events that last for multiple frames.

- Panning is a Ctrl+Click-Drag
- Teleport (or pulling on the player) is a Shift+Click-Drag

The key modifiers and specific mouse buttons might change. But these will always be a
click-drag. It is simpler to just query the mouse position here than to use the mouse motion
events.

Details
OngoingAction is a helper struct to organize Game.

OngoingAction tracks panning and similar mouse actions:
    - mouse panning state -- see Panning
    - click-drag player teleport -- OngoingAction.drag_player_is_active

Tracking state is necessary for these sustained actions. Just handling events is insufficient.
For example, while Shift + left-mouse-button are held, drag the player around the screen. We can
detect when Shift is pressed and released and when the left-mouse-button is pressed and
released. But we need to track those states to know that the action is ongoing in the game loop
iterations after the press and before the release.
"""

import pygame
from src.context import Context, namespace
from engine.geometry_types import Point2D, DirectedLineSeg2D


@namespace
class OngoingAction:
    """Actions that last for multiple frames such as click-drag.

    Usage:
        from gamelibs.ongoing_action import OngoingAction

        @dataclass
        class Game:
            ...
            ongoing_action: OngoingAction = OngoingAction()
            ...
            def loop(self) -> None:
                ...
                UI.consume_event_queue()  # Iterate over all user events
                self.ongoing_action.update(self)
    """

    drag_player_is_active: bool = False

    @classmethod
    def update(cls) -> None:
        """Update all ongoing actions."""
        cls.drag_player()

    @classmethod
    def drag_player(cls) -> None:
        """Teleport player to mouse, like pulling on player and NPCs."""
        # if game.input_mapper.ongoing_action.drag_player_is_active:
        if cls.drag_player_is_active:
            # Get mouse position in game coordinates
            mouse_p = Point2D.from_tuple(pygame.mouse.get_pos())
            mouse_g = Context.game.coord_sys.xfm(
                    mouse_p.as_vec(),
                    Context.game.coord_sys.matrix.pcs_to_gcs
                    ).as_point()
            player_to_mouse = DirectedLineSeg2D(
                    start=Context.game.entities["player"].origin,
                    end=mouse_g)
            # Teleport NPC2 to mouse
            Context.game.entities["cross2"].origin = player_to_mouse.parametric_point(1.0)
            # Teleport NPC1 to half-way between player and NPC2
            Context.game.entities["cross1"].origin = player_to_mouse.parametric_point(0.5)
