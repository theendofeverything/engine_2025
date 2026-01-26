#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Game kata 2025-11-17

* [x] Fill the screen with a color
    * This required that I:
        * store the Surface returned by pygame.display.set_mode in the Game
            * Update 2026-01-01: No. Use pygame-ce instead of pygame and create a pygame.Window.
        * pass the Game to loop()
* [x] Draw something on the screen
    * I drew a line using pygame.draw.line()
* [x] Replace pygame.color.Color() with named colors:
    * Create a library of named colors: Colors.name1, Colors.name2, etc.
* [x] Render some text
* [x] Render mouse position
    [x] Create shortcut ;kpg to open local copy of pygame docs in browser
* [x] Render FPS and milliseconds per frame
* [x] Track window size
    * [x] Handle window resize events
    * [x] Capture new window size
* [x] Track mouse zoom
    * [x] Zoom at a point: calculate a translation vector based on the location of the zoom. Get the
    mouse location, convert to GCS, then after the zoom increment, convert the mouse coordinate to
    GCS again. Use the two GCS points to get a vector. Convert that vector to pixel coordinates
    (this was tricky to figure out), then offset the PCS origin by that vector so that the screen
    pans just the right amount to keep that mouse position at the center.
* [x] Track mouse pan
    * [x] Catch events for mouse button press and release
    * [x] Track whether mouse button 1 is up/down
    * [x] Track where pan starts and ends
    * [x] Calculate the panning vector
    * [x] Define translation and panning vectors as properties (values returned by function)
    * [x] Update the origin when panning ends
    * [x] Update the origin when screen is resized
* [x] Replace pixel coordinates with world space coordinates
    * [x] Create high-school algebra transforms to map from world space to
          pixel space
    * [x] Draw in GCS then render in PCS
    * [x] Eliminate hard-coded values in the transforms
        * [x] Hard-coded scaling factor screen_width/2 becomes screen_width/gcs_width
              where gcs_width is adjusted on mouse zoom
        * [x] Hard-coded translation screen_xy/2 must get updated on zoom and on pan
    * [x] Create matrix algebra transforms
        * [x] Create gcs_to_pcs
        * [x] Document this
        * [x] Calculate matrix inverse of a 2x2 augmented with homogeneous coordinates
* [x] Calculate matrix inverse of a general 3x3
* [x] Make 'engine' reusable with any 'game':
    * Pull 'engine/game.py' out of `engine/` and up one level
    * Leave `main.py` as-is (it launches game but is not specific to any game)
    * Intent is to use `game.py` as a starting point in writing games.
* [x] Simplify debug HUD variable snapshots
* [x] Create a BufferInt to buffer the display of FPS in the HUD.
* [x] Add animation to the artwork: see 'Art.randomize_line' and 'Game.draw_a_cross'.
* [x] Replace code using 'pygame.display'
    * Use the pygame-ce version: 'window = pygame.Window', 'window_surface = window.get_surface()'
    * Then 'pygame.display.flip()' becomes 'window.flip()'
    * Then 'pygame.display.get_window_size()' becomes 'game.renderer.window.size'
* [ ] Set up a Makefile recipe to run doctests only for the active Vim buffer
* [x] Control the speed of the animation using a ClockedEvent.
    * [ ] Animation state persists across frames, even when the Entity is moving
* [x] Change the structure of Timing for counting frames:
    * Timing has a dict of FrameCounters with keys 'game' and 'video'
    * Each FrameCounter has a dict of ClockedEvents.
    * Each ClockedEvent tracks whether its period has elapsed
    * [ ] If the FrameCounter is paused when a ClockedEvent has a whole number of frames, Entities
      using the ClockedEvent do not keep getting clocked on every video frame (how did I set this
      up?)
* [x] Add a playable character (something the user can move around).
* [ ] Use enum.Flag for tracking entity movement up/down/left/right
* [ ] Add collision detection.
* [ ] Make window opacity user-controllable
* [ ] Improve debug HUD:
    * [ ] Provide ability to color debug HUD text to make it easier to notice special values.
    * [ ] Put a transparent background behind the debug hud so that it is easier to read.
    * [ ] Standardize HUD formatting:
        * [ ] Use left-aligned formatting to create tables
        * [ ] Make a syntax for displaying a tree structure of data
    * [ ] Make HUD interactive:
        * [ ] Keyboard/mouse interactions to collapse/expand tree nodes
* [ ] Improve frame rate metrics:
    * [ ] Display average FPS instead of displaying one value every 30 frames
    * [ ] Display the percentage of the game loop period that is utilized
"""

from dataclasses import dataclass, field
import sys
from enum import Enum, auto
import random
import pathlib
import logging
import pygame
from engine.debug import Debug
from engine.timing import Timing, FrameCounter, ClockedEvent
from engine.art import Art
from engine.ui import UI
from engine.panning import Panning
from engine.coord_sys import CoordinateSystem
from engine.renderer import Renderer
from engine.geometry_types import Point2D, Vec2D
from engine.drawing_shapes import Cross
from engine.colors import Colors
from engine.entity import Entity, EntityType

FILE = pathlib.Path(__file__).name


class Action(Enum):
    """Enumerate all actions for the InputMapper."""
    QUIT = auto()
    CLEAR_DEBUG_SNAPSHOT_ARTWORK = auto()
    TOGGLE_DEBUG_ART_OVERLAY = auto()
    TOGGLE_FULLSCREEN = auto()
    TOGGLE_DEBUG_HUD = auto()
    TOGGLE_PAUSE = auto()
    FONT_SIZE_INCREASE = auto()
    FONT_SIZE_DECREASE = auto()
    CONTROLS_ADJUST_K_LESS = auto()
    CONTROLS_ADJUST_K_MORE = auto()
    CONTROLS_ADJUST_B_LESS = auto()
    CONTROLS_ADJUST_B_MORE = auto()
    CONTROLS_PICK_MODE_1 = auto()
    CONTROLS_PICK_MODE_2 = auto()
    CONTROLS_PICK_MODE_3 = auto()


@dataclass
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod): Action}

    >>> input_mapper = InputMapper()
    >>> key_map = input_mapper.key_map
    >>> key_map
    {(99, 0): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
    (100, 0): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,
    (98, 3): <Action.CONTROLS_ADJUST_B_LESS: 11>,
    (98, 0): <Action.CONTROLS_ADJUST_B_MORE: 12>,
    (107, 3): <Action.CONTROLS_ADJUST_K_LESS: 9>,
    (107, 0): <Action.CONTROLS_ADJUST_K_MORE: 10>,
    (49, 0): <Action.CONTROLS_PICK_MODE_1: 13>,
    (50, 0): <Action.CONTROLS_PICK_MODE_2: 14>,
    (51, 0): <Action.CONTROLS_PICK_MODE_3: 15>,
    (113, 0): <Action.QUIT: 1>,
    (32, 0): <Action.TOGGLE_PAUSE: 6>,
    (1073741892, 0): <Action.TOGGLE_FULLSCREEN: 4>,
    (1073741893, 0): <Action.TOGGLE_DEBUG_HUD: 5>,
    (61, 195): <Action.FONT_SIZE_INCREASE: 7>,
    (45, 192): <Action.FONT_SIZE_DECREASE: 8>}
    """
    key_map: dict[tuple[int, int], Action] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # TODO: I put all variations of left and right SHIFT and CTRL keys but this is insanity.
        # There has to be a better way.
        self.key_map = {
                (pygame.K_c, pygame.KMOD_NONE): Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK,
                (pygame.K_d, pygame.KMOD_NONE): Action.TOGGLE_DEBUG_ART_OVERLAY,
                (pygame.K_b, pygame.KMOD_SHIFT): Action.CONTROLS_ADJUST_B_LESS,
                (pygame.K_b, pygame.KMOD_LSHIFT): Action.CONTROLS_ADJUST_B_LESS,
                (pygame.K_b, pygame.KMOD_RSHIFT): Action.CONTROLS_ADJUST_B_LESS,
                (pygame.K_b, pygame.KMOD_NONE): Action.CONTROLS_ADJUST_B_MORE,
                (pygame.K_k, pygame.KMOD_SHIFT): Action.CONTROLS_ADJUST_K_LESS,
                (pygame.K_k, pygame.KMOD_LSHIFT): Action.CONTROLS_ADJUST_K_LESS,
                (pygame.K_k, pygame.KMOD_RSHIFT): Action.CONTROLS_ADJUST_K_LESS,
                (pygame.K_k, pygame.KMOD_NONE): Action.CONTROLS_ADJUST_K_MORE,
                (pygame.K_1, pygame.KMOD_NONE): Action.CONTROLS_PICK_MODE_1,
                (pygame.K_2, pygame.KMOD_NONE): Action.CONTROLS_PICK_MODE_2,
                (pygame.K_3, pygame.KMOD_NONE): Action.CONTROLS_PICK_MODE_3,
                (pygame.K_q, pygame.KMOD_NONE): Action.QUIT,
                (pygame.K_SPACE, pygame.KMOD_NONE): Action.TOGGLE_PAUSE,
                (pygame.K_F11, pygame.KMOD_NONE): Action.TOGGLE_FULLSCREEN,
                (pygame.K_F12, pygame.KMOD_NONE): Action.TOGGLE_DEBUG_HUD,
                (pygame.K_EQUALS, pygame.KMOD_SHIFT | pygame.KMOD_CTRL): Action.FONT_SIZE_INCREASE,
                (pygame.K_EQUALS, pygame.KMOD_LSHIFT | pygame.KMOD_CTRL): Action.FONT_SIZE_INCREASE,
                (pygame.K_EQUALS, pygame.KMOD_RSHIFT | pygame.KMOD_CTRL): Action.FONT_SIZE_INCREASE,
                (pygame.K_EQUALS, pygame.KMOD_SHIFT | pygame.KMOD_LCTRL): Action.FONT_SIZE_INCREASE,
                (pygame.K_EQUALS, pygame.KMOD_LSHIFT | pygame.KMOD_LCTRL): Action.FONT_SIZE_INCREASE,
                (pygame.K_EQUALS, pygame.KMOD_RSHIFT | pygame.KMOD_LCTRL): Action.FONT_SIZE_INCREASE,
                (pygame.K_EQUALS, pygame.KMOD_SHIFT | pygame.KMOD_RCTRL): Action.FONT_SIZE_INCREASE,
                (pygame.K_EQUALS, pygame.KMOD_LSHIFT | pygame.KMOD_RCTRL): Action.FONT_SIZE_INCREASE,
                (pygame.K_EQUALS, pygame.KMOD_RSHIFT | pygame.KMOD_RCTRL): Action.FONT_SIZE_INCREASE,
                (pygame.K_MINUS, pygame.KMOD_CTRL): Action.FONT_SIZE_DECREASE,
                (pygame.K_MINUS, pygame.KMOD_LCTRL): Action.FONT_SIZE_DECREASE,
                (pygame.K_MINUS, pygame.KMOD_RCTRL): Action.FONT_SIZE_DECREASE,
                }


# pylint: disable=too-many-instance-attributes
@dataclass
class Game:
    """Top-level game code.

    Game data is shared by all the code.

    Abbreviations:
        GCS: Game Coordinate System
        PCS: Pixel Coordinate System
        xfm: transform

    Suffix abbreviations:
        h:  homogeneous coordinates
        _g: GCS
        _p: PCS

    Game code is divided up as follows:
    >>> game = Game(log=None)
    >>> game
    Game(log=None,
         input_mapper=InputMapper(...),
         debug=Debug(...),
         timing=Timing(...),
         art=Art(...),
         renderer=Renderer(...),
         ui=UI(...),
         coord_sys=CoordinateSystem(...),
         entities={...})
    """
    # Instance variables defined in the implicit __init__()
    log:        logging.Logger  # log created in main.py
    input_mapper: InputMapper = InputMapper()  # Map inputs to actions
    debug:      Debug = Debug()     # Display debug prints in HUD and overlay debug art
    timing:     Timing = Timing()   # Set up a clock to set frame rate and measure frame period
    art:        Art = Art()         # Set up all artwork for rendering

    # Instance variables defined in __post_init__()
    renderer:   Renderer = field(init=False)
    ui:         UI = field(init=False)                      # Keyboard, mouse, panning, zoom
    coord_sys:  CoordinateSystem = field(init=False)        # Track state of PCS and GCS
    entities:   dict[str, Entity] = field(init=False)   # Game characters like the player

    def __post_init__(self) -> None:
        # Load pygame
        pygame.init()
        pygame.font.init()
        self.debug_font = "fonts/ProggyClean.ttf"

        # Handle rendering in renderer.py
        # Note: The window size is just an initial value.
        #   On WINDOWSIZECHANGED events, the window size and the software rendering
        #   Surface size will automatically adjust to the new size value.
        #   It is not necessary to create a new window_surface with the new window size.
        #   See handle_windowsizechanged_events.
        self.renderer = Renderer(game=self)
        self.renderer.window.title = "Example game"
        # self.renderer.window.size = (60*16, 60*9)
        # self.renderer.window.size = (60*16, 60*14)
        self.renderer.window.size = (700, 700)
        self.renderer.window.resizable = True
        # Additional window settings used during development:
        self.renderer.window.always_on_top = True
        # self.renderer.window.position = (950, 0)
        self.renderer.window.position = (0, 0)
        # self.renderer.window.opacity = 0.8              # This is neat
        # self.renderer.toggle_fullscreen()               # Start in fullscreen

        # Handle all user interface events in ui.py (keyboard, mouse, panning, zoom)
        self.ui = UI(game=self, panning=Panning())
        self.ui.subscribe(self.ui_callback_to_map_event_to_action)

        # Set the GCS to fit the window size and center the GCS origin in the window.
        self.coord_sys = CoordinateSystem(
                window_size=Vec2D.from_tuple(self.renderer.window.size),
                panning=self.ui.panning)

        #######################
        # Create clocked events
        #######################
        # Add a FrameCounter for the game.
        self.timing.frame_counters["game"] = FrameCounter()
        # Add ClockedEvents to the frame counter.
        frame_counter = self.timing.frame_counters["game"]
        frame_counter.clocked_events["every_frame"] = ClockedEvent(
                frame_counter,
                period=1
                )
        frame_counter.clocked_events["period_1"] = ClockedEvent(
                frame_counter,
                period=1
                )
        frame_counter.clocked_events["period_2"] = ClockedEvent(
                frame_counter,
                period=2
                )
        frame_counter.clocked_events["period_3"] = ClockedEvent(
                frame_counter,
                period=3
                )
        frame_counter.clocked_events["period_n"] = ClockedEvent(
                frame_counter,
                period=20
                )
        for name, clocked_event in frame_counter.clocked_events.items():
            clocked_event.event_name = name

        ###################################
        # Create entities (like the Player)
        ###################################
        # size: Use entity size as mass and include mass in the acceleration calc
        # clocked_event_name: controls animation speed
        # origin: set initial location
        self.entities = {}
        self.entities["player"] = Entity(
                debug=self.debug,
                entities=self.entities,
                entity_type=EntityType.PLAYER,
                clocked_event_name="period_3",
                # origin=Point2D(0.5, 0),
                )
        self.entities["cross1"] = Entity(
                debug=self.debug,
                entities=self.entities,
                entity_type=EntityType.NPC,
                clocked_event_name="period_3",
                # clocked_event_name="period_1",
                # origin=Point2D(0, 0.25),
                )
        self.entities["cross2"] = Entity(
                debug=self.debug,
                entities=self.entities,
                entity_type=EntityType.NPC,
                clocked_event_name="period_3",
                size=0.15,
                # clocked_event_name="period_1",
                # origin=Point2D(0, -0.5),
                )
        # Entities track their own name for display in the debug HUD
        for name, entity in self.entities.items():
            entity.entity_name = name

        # Set NPC to follow the player
        self.entities["cross1"].movement.follow_entity = "player"
        self.entities["cross2"].movement.follow_entity = "cross1"

    def run(self) -> None:
        """Run the game."""
        log = self.log
        log.debug(f"Window supports OpenGL: {self.renderer.window.opengl}")
        log.debug(f"Entities: {self.entities}")
        while True:
            self.loop(log)

    def loop(self, log: logging.Logger) -> None:
        """Loop until the user quits."""
        # Prologue: reset debug
        self.debug.hud.reset()                          # Clear the debug HUD
        self.debug_hud_begin()                          # Load first values in debug HUD
        # Game
        self.reset_art()                                # Clear old art
        self.ui.handle_events(log)                      # Handle all user events
        self.update_entities()                          #
        self.draw_remaining_art()                       # Draw any remaining art not already drawn
        # Epilogue: update debug HUD, display, and timing
        self.update_frame_counters()                    # Advance frame-based ticks
        self.debug.display_snapshots_in_hud()           # Print snapshots in HUD last
        self.renderer.render_all()                      # Render all art and HUD
        self.timing.maintain_framerate(fps=60)          # Run at 60 FPS

    def ui_callback_to_map_event_to_action(self, event: pygame.event.Event, kmod: int) -> None:
        """Map UI events to actions and then passes the action to the action handler.

        Usage:
            1. Register with the UI like this:
                self.ui = UI(game=self, ...)  # Instantiate UI
                ...
                ui = self.ui
                ui.subscribe(ui_callback_to_map_event_to_action)  # Register callback
            2. Define actions in the InputMapper.key_map
            3. Define how to handle the actions in _handle_action_events()

        This is a callback registered with UI. It simply maps events from the pygame event queue to
        actions and then passes the action to the action handler.

        Actions are defined in the InputMapper.key_map:
            {(99, 0): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
            (100, 0): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,
            ...

            The dictionary key (int, int) is the tuple (event.key, kmod) where:
                - event.key is the int key code of the key press
                - kmod is the int of the bitfield representing which key modifiers are held,
                  returned by pygame.key.get_mods()

        Even with no key modifiers held down, kmod is 4096, not 0. I only care about ALT, CTRL, and
        SHIFT, so I filter the kmod before using it by masking it with ALT | CTRL | SHIFT.

        I use dict.get((event.key, kmod)) to get the action corresponding to the key press. Unlike
        key_map[(event.key, kmod)], get() does not throw an exception if the tuple does not exist in
        InputMapper.key_map. If the tuple does not exist, dict.get() returns None.
        """
        key_map = self.input_mapper.key_map
        log = self.log
        match event.type:
            # TODO: I have to hold down both SHIFT keys to get pygame.KMOD_SHIFT. How should I set
            # this up so that either left or right SHIFT keys register as SHIFT?
            case pygame.KEYDOWN:
                log.debug(f"Keydown: {event}")
                log.debug(f"kmod: {kmod}")
                # Filter out irrelevant keymods
                kmod = kmod & (pygame.KMOD_ALT | pygame.KMOD_CTRL | pygame.KMOD_SHIFT)
                log.debug(f"Filtered kmod: {kmod}")
                action = key_map.get((event.key, kmod))
                if action is not None:
                    self._handle_action_events(action)

    # pylint: disable=too-many-branches
    def _handle_action_events(self, action: Action) -> None:
        """Handle actions events detected by the UI"""
        log = self.log
        game = self
        match action:
            case Action.QUIT:
                log.debug("User action: quit.")
                sys.exit()
            case Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK:
                log.debug("User action: clear debug snapshot artwork.")
                game.debug.art.reset_snapshots()
            case Action.TOGGLE_FULLSCREEN:
                log.debug("User action: toggle fullscreen.")
                game.renderer.toggle_fullscreen()
            case Action.TOGGLE_DEBUG_HUD:
                log.debug("User action: toggle debug HUD.")
                game.debug.hud.is_visible = not game.debug.hud.is_visible
            case Action.TOGGLE_PAUSE:
                log.debug("User action: toggle pause.")
                game.timing.frame_counters["game"].toggle_pause()
                game_is_paused = game.timing.frame_counters["game"].is_paused
                game.debug.snapshots["pause"] = ("game.timing.frame_counters['game'].is_paused: "
                                                 f"{game_is_paused}")
            case Action.TOGGLE_DEBUG_ART_OVERLAY:
                log.debug("User action: toggle debug art overlay.")
                game.debug.art.is_visible = not game.debug.art.is_visible
            case Action.FONT_SIZE_INCREASE:
                game.debug.hud.font_size.increase()
                log.debug("User action: Increase debug HUD font size."
                          f"Font size: {game.debug.hud.font_size.value}.")
            case Action.FONT_SIZE_DECREASE:
                game.debug.hud.font_size.decrease()
                log.debug(f"User action: Decrease debug HUD font size."
                          f"Font size: {game.debug.hud.font_size.value}.")
            # TEMPORARY CODE FOR WORKING ON NPC MOTION
            case Action.CONTROLS_ADJUST_K_LESS:
                game.debug.hud.controls["k"] /= 2
            case Action.CONTROLS_ADJUST_K_MORE:
                game.debug.hud.controls["k"] *= 2
            case Action.CONTROLS_ADJUST_B_LESS:
                game.debug.hud.controls["b"] /= 2
            case Action.CONTROLS_ADJUST_B_MORE:
                game.debug.hud.controls["b"] *= 2
            # Set spring constant and damping: three modes.
            case Action.CONTROLS_PICK_MODE_1:
                log.debug("User action: Select mode 1 -- springy linked motion")
                game.debug.hud.controls["k"] = 0.04
                game.debug.hud.controls["b"] = 0.064
            case Action.CONTROLS_PICK_MODE_2:
                log.debug("User action: Select mode 2 -- rigid linked motion")
                game.debug.hud.controls["k"] = 1.28
                game.debug.hud.controls["b"] = 0.512
            case Action.CONTROLS_PICK_MODE_3:
                log.debug("User action: Select mode 3 -- separate entities following motion")
                game.debug.hud.controls["k"] = 0.005
                game.debug.hud.controls["b"] = 0.064

    def update_frame_counters(self) -> None:
        """Update the frame tick counters (animations are clocked by frame ticks).

        Video frames always update.
        Game frames only update if the game is not paused.
        """
        timing = self.timing
        for frame_counter in timing.frame_counters.values():
            frame_counter.update()

        debug = True

        def debug_frame_counters() -> None:
            hud = self.debug.hud
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
        if debug: debug_frame_counters()

    def update_entities(self) -> None:
        """Update the state of all entities based on counters and events."""
        ui_keys = self.ui.keys
        timing = self.timing
        art = self.art
        # TODO: make the red cross (slowly) follow the player around. Adust movement by adusting
        # speed vector, not direct movement (to simulate inertia).
        for entity in self.entities.values():
            entity.update(timing, ui_keys)
            entity.draw(art)

        debug = True
        if debug:
            def debug_entities() -> None:
                hud = self.debug.hud
                heading = f"|\n+- Entities ({FILE})"
                hud.print(heading)

                iterate_over_specific_entity_attrs = True
                if iterate_over_specific_entity_attrs:
                    # Only show these entity attrs:
                    for name, entity in self.entities.items():
                        hud.print(f"|     +- {name}")
                        hud.print(f"|        +- name: {entity.entity_name}")
                        hud.print(f"|        +- type: {entity.entity_type}")
                        hud.print(f"|        +- clocked by: {entity.clocked_event_name}")
                        hud.print(f"|        +- origin: {entity.origin}")
                        hud.print(f"|        +- size: {entity.size}")
                        hud.print(f"|        +- amount_excited: {entity.amount_excited}")
                else:
                    for entity_name, entity_value in self.entities.items():
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
            debug_entities()

    def reset_art(self) -> None:
        """Clear out old artwork: application and debug."""
        self.art.reset()                                # Reset application artwork
        self.debug.art.reset()                          # Clear the debug artwork

    def draw_remaining_art(self) -> None:
        """Update art and debug art"""
        draw_more_stuff = False
        if draw_more_stuff:
            # self.draw_a_cross()                       # Draw application artwork
            self.draw_background_crosses()                      # Draw application artwork
            # self.draw_debug_crosses()                   # Draw debug artwork

    def debug_hud_begin(self) -> None:
        """The first values displayed in the HUD are printed in this function."""
        debug = self.debug
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

        def debug_fps() -> None:
            """Display frame duration in milliseconds and rate in FPS."""
            timing = self.timing
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

        def debug_window_size() -> None:
            """Display window size and center."""
            debug.hud.print(f"|\n+- OS window (in pixels) ({FILE})")
            coord_sys: CoordinateSystem = self.coord_sys
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

        debug_fps()
        debug_window_size()
        debug.hud.print("\n------")
        debug.hud.print(f"Locals ({FILE})")         # Local debug prints (e.g., from UI)
        debug.hud.print("------")

    def draw_background_crosses(self) -> None:
        """Draw some animated shapes in the background.

        Note: Framerate tanks when I zoom out too far -- zooming increases number of crosses because
        gcs_width changes. My temporary fix here is to clamp the max number of crosses, but I have a
        new problem that the origins of the crosses changes when I zoom. That is the problem with
        attempting to just draw these without any persistent state.

        TODO: make these animated shapes Entities so that I can give the a persistent state: slow
        down their animation speeds and assign different amount sof drift to each dependent on the
        location of the player character.
        """
        coord_sys = self.coord_sys
        crosses: list[Cross] = []
        # Put a cross every 0.2 units.
        #
        # Example:
        # 2 GCS units
        # ---------         = 10 crosses
        # 0.2 units/cross
        dist = Vec2D(x=0.2, y=0.4)
        # Limit the crosses to a 4x4 to avoid framerate tanking when zoomed way out.
        num_crosses_x = round(min(coord_sys.gcs_width, 4) / dist.x)
        num_crosses_y = round(min(coord_sys.gcs_width, 4) / dist.y)
        start = Point2D(x=-1*coord_sys.gcs_width/2,
                        y=-1*coord_sys.gcs_width/2)
        drift_amt = random.uniform(0.002, 0.05)
        drift = Vec2D(x=random.uniform(-1*drift_amt, drift_amt),
                      y=random.uniform(-1*drift_amt, drift_amt))
        # Drift each cross a random amount and append randomized line artwork to art.lines
        for i in range(num_crosses_x):
            for j in range(num_crosses_y):
                crosses.append(Cross(
                    origin=Point2D(start.x + i*dist.x + drift.x, start.y + j*dist.y + drift.y),
                    size=0.1,
                    rotate45=False,
                    color=Colors.line))  # color=Colors.background_lines))
        # Append randomized line artwork to art.lines
        wiggle = 0.005
        for cross in crosses:
            for line in cross.lines:
                # Randomize the line before appending it
                wiggle_line = self.art.randomize_line(line, wiggle)
                self.art.lines.append(wiggle_line)

    def draw_debug_crosses(self) -> None:
        """Draw a debug cross at the origin and at the player."""
        # Create debug artwork that uses lines
        crosses: list[Cross] = [
                Cross(origin=Point2D(0, 0),
                      size=0.1,
                      color=Colors.line_debug),
                Cross(origin=self.entities["player"].origin,
                      size=0.1,
                      rotate45=True,
                      color=Colors.line_debug),
                ]
        # Copy the line artwork to debug.art.lines
        for cross in crosses:
            for line in cross.lines:
                self.debug.art.lines_gcs.append(line)
