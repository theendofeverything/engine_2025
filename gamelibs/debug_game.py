#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Debug game code using the debug engine.
"""

from dataclasses import dataclass, field
import pathlib
from enum import Enum, auto
import pygame
from engine.coord_sys import CoordinateSystem
from engine.geometry_types import Point2D, Vec2D
from engine.colors import Colors
from engine.drawing_shapes import Line2D

FILE = pathlib.Path(__file__).name


class Mode(Enum):
    """Enumerate "modes" selected with the number keys."""
    MODE_1 = auto()
    MODE_2 = auto()
    MODE_3 = auto()


@dataclass
class DebugGame:
    """Debug game code."""
    game: "Game"
    mode: Mode = Mode.MODE_2
    controls:   dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.define_controls()

    def define_controls(self) -> None:
        """Define variables that connect to user input from the HUD."""
        # TODO: use case match to set the following based on the default Mode
        # Nice springy motion
        # self.controls["k"] = 0.04
        # self.controls["b"] = 0.064
        # Nice linked motion
        self.controls["k"] = 1.28
        self.controls["b"] = 0.512
        # Nice following motion
        # self.controls["k"] = 0.005
        # self.controls["b"] = 0.064

    def hud_begin(self) -> None:
        """The first values displayed in the HUD are printed in this function."""
        debug = self.game.debug
        debug_hud = f"Debug HUD ({FILE})"
        # Version values
        using_pygame_ce = getattr(pygame, "IS_CE", False)
        pygame_version = f"pygame{'-ce' if using_pygame_ce else ''} {pygame.version.ver}"
        sdl_version = f"SDL {pygame.version.SDL}"
        # Debug values
        debug_hud_font_size = f"debug.hud.font_size:      {debug.hud.font_size.value}"
        debug_art_is_visible = f"debug.hud.art.is_visible: {debug.art.is_visible} ('d' to toggle)"
        debug.hud.print(f"{debug_hud:<25}"
                        f"{pygame_version:<25}"
                        f"{debug_hud_font_size:<25}")
        debug.hud.print(f"{'---------':<25}"
                        f"{sdl_version:<25}"
                        f"{debug_art_is_visible:<25}")

        # debug.hud.print("\n------")
        # debug.hud.print(f"Locals ({FILE})")         # Local debug prints (e.g., from UI)
        # debug.hud.print("------")

    def fps(self, show_in_hud: bool) -> None:
        """Display frame duration in milliseconds and rate in FPS."""
        if not show_in_hud: return
        debug = self.game.debug
        timing = self.game.timing
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
        debug.hud.print(f"|\n+- Video frames ({FILE})")
        debug.hud.print(f"|   +- FPS: {fps:0.1f}")
        debug.hud.print(f"|   +- Period: {ms_per_frame:d}ms")

    def window_size(self, show_in_hud: bool) -> None:
        """Display window size and center."""
        if not show_in_hud: return
        debug = self.game.debug
        coord_sys: CoordinateSystem = self.game.coord_sys
        debug.hud.print(f"|\n+- OS window (in pixels) ({FILE})")
        # Size
        window_size: Vec2D = coord_sys.window_size
        gcs_window_size: Vec2D = coord_sys.xfm(v=window_size, mat=coord_sys.matrix.pcs_to_gcs)
        debug.hud.print(f"|  +- window_size: {window_size.fmt(0.0)} PCS"
                        f", {gcs_window_size} GCS")

        # Center
        window_center: Point2D = coord_sys.window_center
        gcs_window_center: Vec2D = coord_sys.xfm(
                v=window_center.as_vec(),
                mat=coord_sys.matrix.pcs_to_gcs)
        debug.hud.print(f"|  +- window_center: {window_center.fmt(0.0)} PCS"
                        f", {gcs_window_center} GCS")

    def mouse(self, show_in_hud: bool) -> None:
        """Debug mouse position and buttons."""
        if not show_in_hud: return
        debug = self.game.debug
        coord_sys = self.game.coord_sys
        debug.hud.print(f"|\n+- InputMapper -> mouse_pressed ({FILE})")

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
            debug.hud.print(f"|  +- mouse.get_pos(): {mouse_gcs} GCS, {mouse_pcs.fmt(0.0)} PCS")
        debug_mouse_position()

        def debug_mouse_buttons() -> None:
            """Display mouse button state."""
            debug.hud.print("|  +- UI.mouse_pressed.:")
            debug.hud.print(f"|     +- left: {self.game.input_mapper.mouse_pressed.left}")
            debug.hud.print(f"|     +- middle: {self.game.input_mapper.mouse_pressed.middle}")
            debug.hud.print(f"|     +- right: {self.game.input_mapper.mouse_pressed.right}")
        debug_mouse_buttons()

    def player_forces(self, show_in_hud: bool) -> None:
        """Debug key presses for game controls."""
        if not show_in_hud: return
        hud = self.game.debug.hud
        hud.print(f"|\n+- Movement -> PlayerForce ({FILE})")
        player_forces = ""
        entities = self.game.entities
        if entities["player"].movement.player_force.left:
            player_forces += "LEFT"
        if entities["player"].movement.player_force.right:
            player_forces += "RIGHT"
        if entities["player"].movement.player_force.up:
            player_forces += "UP"
        if entities["player"].movement.player_force.down:
            player_forces += "DOWN"
        hud.print(f"|  +- player_forces: {player_forces}")

    def panning(self, show_in_hud: bool) -> None:
        """Draw debug art to show panning and display state/values in HUD"""
        debug = self.game.debug
        panning = self.game.input_mapper.ongoing_action.panning
        if not show_in_hud: return
        coord_sys = self.game.coord_sys
        debug.hud.print(f"|\n+- UI -> Panning (Ctrl+Left-Click-Drag): {panning.is_active} ({FILE})")
        debug.hud.print(f"|        +- .begin: {panning.begin.fmt(0.0)}")
        debug.hud.print(f"|        +- .end: {panning.end.fmt(0.0)}")
        debug.hud.print(f"|        +- .vector: {panning.vector.fmt(0.0)}")
        debug.hud.print("|           +- Panning updates the coord_sys:")
        debug.hud.print(f"|              +- coord_sys.pcs_origin:  {coord_sys.pcs_origin}")
        debug.hud.print(f"|              +- coord_sys.translation: {coord_sys.translation} = "
                        "pcs_origin + .vector")
        if panning.is_active:
            debug.art.lines_pcs.append(
                    Line2D(start=panning.begin, end=panning.end, color=Colors.panning))

    def entities(self, show_in_hud: bool) -> None:
        """Show important attrs for every entity."""
        if not show_in_hud: return
        hud = self.game.debug.hud
        heading = f"|\n+- Entities ({FILE})"
        hud.print(heading)
        entities = self.game.entities

        iterate_over_specific_entity_attrs = True
        if iterate_over_specific_entity_attrs:
            # Only show these entity attrs:
            for name, entity in entities.items():
                hud.print(f"|     +- {name}")
                hud.print(f"|        +- name: {entity.entity_name}")
                hud.print(f"|        +- type: {entity.entity_type}")
                hud.print(f"|        +- clocked by: {entity.clocked_event_name}")
                hud.print(f"|        +- origin: {entity.origin}")
                hud.print(f"|        +- size: {entity.size}")
                hud.print(f"|        +- amount_excited: {entity.amount_excited}")
        else:
            for entity_name, entity_value in entities.items():
                hud.print(f"|  +- {entity_name}:")
                for attr, attr_value in entity_value.__dict__.items():
                    match attr:
                        case "points":
                            # Catch points to print them with desired precision
                            hud.print(f"|     +- {attr}:")
                            for point in attr_value:
                                hud.print(f"|        +- !{point.fmt(0.3)}")
                        case "debug":
                            # Do not iterate over the items in game.debug!
                            pass
                        case "entities":
                            # Do not iterate over the items in game.entities!
                            pass
                        case _:
                            hud.print(f"|     +- {attr}: {attr_value}")

    def frame_counters(self, show_in_hud: bool) -> None:
        """Show frame counters in HUD."""
        if not show_in_hud: return
        hud = self.game.debug.hud
        timing = self.game.timing
        heading = f"|\n+- Timing -> FrameCounter ({FILE})"
        hud.print(heading)
        # Video frame counters
        hud.print("|  +- frame_counters['video']")
        hud.print(f"|     +- frame_count: {timing.frame_counters['video'].frame_count}")
        hud.print("|     +- clocked_events:")
        for clocked_event in timing.frame_counters["video"].clocked_events.values():
            hud.print(f"|        +- {clocked_event}")
        # Game frame counters
        if timing.frame_counters["game"].is_paused:
            paused = "--Paused--"
        else:
            paused = "(<Space> to pause)"
        hud.print("|  +- frame_counters['game']")
        hud.print(f"|     +- frame_count: {timing.frame_counters['game'].frame_count} {paused}")
        hud.print("|     +- clocked_events:")
        for clocked_event in timing.frame_counters["game"].clocked_events.values():
            hud.print(f"|        +- {clocked_event}")

    def mode_controls(self, show_in_hud: bool) -> None:
        """Display the mode controls in the HUD"""
        if not show_in_hud: return
        hud = self.game.debug.hud
        hud.print(f"|\n+- DebugGame.mode: {self.mode}")
        hud.print(f"+- DebugGame.controls: dict[str, float | ] ({FILE})")
        for name, value in self.controls.items():
            hud.print(f"|  +- controls['{name}']: {value}")
