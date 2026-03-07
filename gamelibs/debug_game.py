#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Debug game code using the debug engine.
"""

import pathlib
from enum import Enum, auto
import pygame
from engine.coord_sys import CoordinateSystem
from engine.geometry_types import Point2D, Vec2D
from engine.colors import Colors
from engine.drawing_shapes import Line2D
from engine.debug import Debug
from src.context import Context
from .input_mapper import Mouse, MouseButton, Panning

FILE = pathlib.Path(__file__).name


class Mode(Enum):
    """Enumerate "modes" selected with the number keys."""
    MODE_1 = auto()
    MODE_2 = auto()
    MODE_3 = auto()


# @dataclass
class DebugGame:
    """Debug game code."""
    # game: "Game"
    # game: Game
    mode: Mode = Mode.MODE_2
    controls:   dict[str, float] = {"k": 1.28, "b": 0.512}

    @staticmethod
    def hud_begin() -> None:
        """The first values displayed in the HUD are printed in this function."""
        debug_hud = f"Debug HUD ({FILE})"
        # Version values
        using_pygame_ce = getattr(pygame, "IS_CE", False)
        pygame_version = f"pygame{'-ce' if using_pygame_ce else ''} {pygame.version.ver}"
        sdl_version = f"SDL {pygame.version.SDL}"
        # Debug values
        debug_hud_font_size = f"Debug.hud.font_size:      {Debug.hud.font_size.value}"
        debug_art_is_visible = f"Debug.hud.art.is_visible: {Debug.art.is_visible} ('d' to toggle)"
        Debug.hud.print(f"{debug_hud:<25}"
                        f"{pygame_version:<25}"
                        f"{debug_hud_font_size:<25}")
        Debug.hud.print(f"{'---------':<25}"
                        f"{sdl_version:<25}"
                        f"{debug_art_is_visible:<25}")

        # Debug.hud.print("\n------")
        # Debug.hud.print(f"Locals ({FILE})")         # Local debug prints (e.g., from UI)
        # Debug.hud.print("------")

    @staticmethod
    def fps(show_in_hud: bool) -> None:
        """Display frame duration in milliseconds and rate in FPS."""
        if not show_in_hud: return
        timing = Context.game.timing
        # # Old: use get_fps() -- it averages every 10 frames
        # fps = timing.clock.get_fps()
        # if timing.ticks["video"].counters["hud_fps"].clocked:
        if timing.frame_counters["video"].clocked_events["hud_fps"].is_period:
            # Update buffered milliseconds per frame once every period (30 frames).
            # See Tick.counters["hud_fps"] and Tick.update() for period.
            timing.update_buffered_ms_per_frame()
        # Print buffered versions to HUD
        fps = timing.fps_buffered
        ms_per_frame = timing.ms_per_frame_buffered
        Debug.hud.print(f"|\n+- Video frames ({FILE})")
        Debug.hud.print(f"|   +- FPS: {fps:0.1f}")
        Debug.hud.print(f"|   +- Period: {ms_per_frame:d}ms")

    @staticmethod
    def window_size(show_in_hud: bool) -> None:
        """Display window size and center."""
        if not show_in_hud: return
        coord_sys: CoordinateSystem = Context.game.coord_sys
        Debug.hud.print(f"|\n+- OS window (in pixels) ({FILE})")
        # Size
        window_size: Vec2D = coord_sys.window_size
        gcs_window_size: Vec2D = coord_sys.xfm(v=window_size, mat=coord_sys.matrix.pcs_to_gcs)
        Debug.hud.print(f"|  +- window_size: {window_size.fmt(0.0)} PCS"
                        f", {gcs_window_size} GCS")

        # Center
        window_center: Point2D = coord_sys.window_center
        gcs_window_center: Vec2D = coord_sys.xfm(
                v=window_center.as_vec(),
                mat=coord_sys.matrix.pcs_to_gcs)
        Debug.hud.print(f"|  +- window_center: {window_center.fmt(0.0)} PCS"
                        f", {gcs_window_center} GCS")

    @staticmethod
    def mouse(show_in_hud: bool) -> None:
        """Debug mouse position and buttons."""
        if not show_in_hud: return
        coord_sys = Context.game.coord_sys
        Debug.hud.print(f"|\n+- Mouse -> is_pressed ({FILE})")

        def debug_mouse_position() -> None:
            """Display mouse position in GCS and PCS."""
            # Get mouse position in pixel coordinates
            mouse_position = Point2D.from_tuple(pygame.mouse.get_pos())
            # Get mouse position in game coordinates
            mouse_gcs = coord_sys.xfm(
                    mouse_position.as_vec(),
                    coord_sys.matrix.pcs_to_gcs)
            # Test transform by converting back to pixel coordinates
            mouse_pcs = coord_sys.xfm(
                    mouse_gcs,
                    coord_sys.matrix.gcs_to_pcs)
            Debug.hud.print(f"|  +- mouse.get_pos(): {mouse_gcs} GCS, {mouse_pcs.fmt(0.0)} PCS")
        debug_mouse_position()

        def debug_mouse_buttons() -> None:
            """Display mouse button state."""
            Debug.hud.print("|  +- Mouse.is_pressed():")
            mouse_button = MouseButton.LEFT
            Debug.hud.print(f"|     +- {mouse_button.name}: {Mouse.is_pressed(mouse_button)}")
            mouse_button = MouseButton.MIDDLE
            Debug.hud.print(f"|     +- {mouse_button.name}: {Mouse.is_pressed(mouse_button)}")
            mouse_button = MouseButton.RIGHT
            Debug.hud.print(f"|     +- {mouse_button.name}: {Mouse.is_pressed(mouse_button)}")
            # The WHEELUP and WHEELDOWN are always False. Why?
            mouse_button = MouseButton.WHEELUP
            Debug.hud.print(f"|     +- {mouse_button.name}: {Mouse.is_pressed(mouse_button)}")
            mouse_button = MouseButton.WHEELDOWN
            Debug.hud.print(f"|     +- {mouse_button.name}: {Mouse.is_pressed(mouse_button)}")
        debug_mouse_buttons()

    @staticmethod
    def player_forces(show_in_hud: bool) -> None:
        """Debug key presses for game controls."""
        if not show_in_hud: return
        Debug.hud.print(f"|\n+- Movement -> PlayerForce ({FILE})")
        player_forces = ""
        entities = Context.game.entities
        if entities["player"].movement.player_force.left:
            player_forces += "LEFT"
        if entities["player"].movement.player_force.right:
            player_forces += "RIGHT"
        if entities["player"].movement.player_force.up:
            player_forces += "UP"
        if entities["player"].movement.player_force.down:
            player_forces += "DOWN"
        Debug.hud.print(f"|  +- player_forces: {player_forces}")

    @staticmethod
    def panning(show_in_hud: bool) -> None:
        """Draw debug art to show panning and display state/values in HUD"""
        if not show_in_hud: return
        coord_sys = Context.game.coord_sys
        Debug.hud.print(f"|\n+- Panning (Ctrl+Left-Click-Drag): {Panning.is_active} ({FILE})")
        Debug.hud.print(f"|        +- .begin: {Panning.begin.fmt(0.0)}")
        Debug.hud.print(f"|        +- .end: {Panning.end.fmt(0.0)}")
        Debug.hud.print(f"|        +- .vector: {Panning.vector().fmt(0.0)}")
        Debug.hud.print("|           +- Panning updates the coord_sys:")
        Debug.hud.print(f"|              +- coord_sys.pcs_origin:  {coord_sys.pcs_origin}")
        Debug.hud.print(f"|              +- coord_sys.translation: {coord_sys.translation} = "
                        "pcs_origin + .vector")
        if Panning.is_active:
            Debug.art.lines_pcs.append(
                    Line2D(start=Panning.begin, end=Panning.end, color=Colors.panning))

    @staticmethod
    def entities(show_in_hud: bool) -> None:
        """Show important attrs for every entity."""
        if not show_in_hud: return
        heading = f"|\n+- Entities ({FILE})"
        Debug.hud.print(heading)
        entities = Context.game.entities

        iterate_over_specific_entity_attrs = True
        if iterate_over_specific_entity_attrs:
            # Only show these entity attrs:
            for name, entity in entities.items():
                Debug.hud.print(f"|     +- {name}")
                Debug.hud.print(f"|        +- name: {entity.entity_name}")
                Debug.hud.print(f"|        +- type: {entity.entity_type}")
                Debug.hud.print(f"|        +- clocked by: {entity.clocked_event_name}")
                Debug.hud.print(f"|        +- origin: {entity.origin}")
                Debug.hud.print(f"|        +- size: {entity.size}")
                Debug.hud.print(f"|        +- amount_excited: {entity.amount_excited}")
        else:
            for entity_name, entity_value in entities.items():
                Debug.hud.print(f"|  +- {entity_name}:")
                for attr, attr_value in entity_value.__dict__.items():
                    match attr:
                        case "points":
                            # Catch points to print them with desired precision
                            Debug.hud.print(f"|     +- {attr}:")
                            for point in attr_value:
                                Debug.hud.print(f"|        +- !{point.fmt(0.3)}")
                        case "debug":
                            # Do not iterate over the items in game.debug!
                            pass
                        case "entities":
                            # Do not iterate over the items in game.entities!
                            pass
                        case _:
                            Debug.hud.print(f"|     +- {attr}: {attr_value}")

    @staticmethod
    def frame_counters(show_in_hud: bool) -> None:
        """Show frame counters in HUD."""
        if not show_in_hud: return
        timing = Context.game.timing
        heading = f"|\n+- Timing -> FrameCounter ({FILE})"
        Debug.hud.print(heading)
        # Video frame counters
        Debug.hud.print("|  +- frame_counters['video']")
        Debug.hud.print(f"|     +- frame_count: {timing.frame_counters['video'].frame_count}")
        Debug.hud.print("|     +- clocked_events:")
        for clocked_event in timing.frame_counters["video"].clocked_events.values():
            Debug.hud.print(f"|        +- {clocked_event}")
        # Game frame counters
        if timing.frame_counters["game"].is_paused:
            paused = "--Paused--"
        else:
            paused = "(<Space> to pause)"
        Debug.hud.print("|  +- frame_counters['game']")
        Debug.hud.print(f"|     +- frame_count: {timing.frame_counters['game'].frame_count}"
                        f"{paused}")
        Debug.hud.print("|     +- clocked_events:")
        for clocked_event in timing.frame_counters["game"].clocked_events.values():
            Debug.hud.print(f"|        +- {clocked_event}")

    @classmethod
    def mode_controls(cls, show_in_hud: bool) -> None:
        """Display the mode controls in the HUD"""
        if not show_in_hud: return
        Debug.hud.print(f"|\n+- DebugGame.mode: {cls.mode}")
        Debug.hud.print(f"+- DebugGame.controls: dict[str, float | ] ({FILE})")
        for name, value in cls.controls.items():
            Debug.hud.print(f"|  +- controls['{name}']: {value}")
