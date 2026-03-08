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
    * Then 'pygame.display.get_window_size()' becomes 'Context.renderer.window.size'
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
* [ ] Move engine code out to game.py via callbacks.
    * game.py grows large, so:
        * [x] create a "gamelibs/" folder and put a "__init__.py" in it to make gamelibs a package
        * [x] move game lib code to gamelibs
        * this package is for user-created libs (not the engine).
* [ ] Document how I am doing callbacks for the UI code
"""

from dataclasses import dataclass, field
import sys
import random
import pathlib
import logging
import pygame
from engine.debug import Debug
from engine.timing import Timing, FrameCounter, ClockedEvent
from engine.art import Art
from engine.ui import UI
from engine.coord_sys import CoordinateSystem
from engine.renderer import Renderer
from engine.geometry_types import Point2D, Vec2D
from engine.drawing_shapes import Cross
from engine.colors import Colors
from engine.entity import Entity, EntityType
from gamelibs.input_mapper import Action, InputMapper, KeyModifier, Panning
from gamelibs.debug_game import DebugGame, Mode
from .context import Context

FILE = pathlib.Path(__file__).name
log = logging.getLogger(__name__)


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
    >>> game = Game()
    >>> game.setup()
    >>> game
    Game(coord_sys=CoordinateSystem(...),
        entities={...},
        debug_font='fonts/ProggyClean.ttf')
    """
    ###################################
    # Engine-defined instance variables
    ###################################
    # Instance variables defined in the implicit __init__() of dataclass
    # Instance variables defined in __post_init__()
    coord_sys:  CoordinateSystem = field(init=False)    # Track state of PCS and GCS
    entities:   dict[str, Entity] = field(init=False)   # Game characters like the player
    debug_font: str = "fonts/ProggyClean.ttf"

    def setup(self) -> None:
        """Setup game data"""
        Context.register_game(self)  # Global access to instance of Game()
        Context.register_renderer(Renderer())  # Global access to instance of Renderer()
        Context.register_timing(Timing())  # Global access to instance of Timing()
        self._create_clocked_events()  # Set up events in Timing that trigger every N frames

        UI.subscribe(self._subscriber_map_event_to_action)  # See _subscriber_map_event_to_action()

        pygame.init()  # Load pygame
        pygame.font.init()  # Load font module

        self._configure_game_window()  # Window renderer config
        # Set the GCS to fit the window size and center the GCS origin in the window.
        self.coord_sys = CoordinateSystem(
                window_size=Vec2D.from_tuple(Context.renderer.window.size)
                )

        self.entities = {}
        self._create_entities(self.entities, self.coord_sys)  # Create entities (like the Player)

    @staticmethod
    def _create_entities(
            entities: dict[str, Entity],
            coord_sys: CoordinateSystem
            ) -> None:
        """Create entities (like the Player)

        Entity parameters
        -----------------
        size: Use entity size as mass and include mass in the acceleration calc
        clocked_event_name: controls animation speed
        origin: set initial location
        """
        entities["player"] = Entity(
                # debug_game=self.debug_game,
                entities=entities,
                entity_type=EntityType.PLAYER,
                clocked_event_name="period_3",
                )
        entities["cross1"] = Entity(
                # debug_game=self.debug_game,
                entities=entities,
                entity_type=EntityType.NPC,
                clocked_event_name="period_3",
                )
        entities["cross2"] = Entity(
                # debug_game=self.debug_game,
                entities=entities,
                entity_type=EntityType.NPC,
                clocked_event_name="period_3",
                size=0.15,
                )
        # Create entities for background art
        # 5 x 5 grid of crosses named "bgnd1" ... "bgnd10"
        size = 0.07
        num_crosses_x = 13
        num_crosses_y = 13
        dist = Vec2D(x=2*size, y=2*size)
        start = Point2D(x=-1*coord_sys.gcs_width/2 + 0.1,
                        y=-1*coord_sys.gcs_width/2 + 0.1)
        for i in range(num_crosses_x):
            for j in range(num_crosses_y):
                number = 1 + j + (i*num_crosses_x)
                name = f"bgnd{number}"
                entities[name] = Entity(
                        # debug_game=self.debug_game,
                        entities=entities,
                        entity_type=EntityType.BACKGROUND_ART,
                        size=size,
                        origin=Point2D(start.x + i*dist.x,
                                       start.y + j*dist.y),
                        )
                me = entities[name]
                # Respond to the player
                me.movement.follow_entities = ["player", "cross1", "cross2"]
                # Be excited in general
                me.amount_excited.low *= 2
                # Get very excited when player is near
                me.amount_excited.high *= 2
        # Entities track their own name for display in the debug HUD
        for name, entity in entities.items():
            entity.entity_name = name

        # Set NPC to follow the player
        entities["cross1"].movement.follow_entity = "player"
        entities["cross2"].movement.follow_entity = "cross1"

    @staticmethod
    def _create_clocked_events() -> None:
        """Add a game FrameCounter to Timing.

        Fill the Timing.FrameCounter with clocked events for various frame periods:

        every_frame: Event is clocked every frame
        period_1: Event is clocked every frame
        period_2: Event is clocked every two frames
        ...
        """
        # Add a FrameCounter for the game.
        Context.timing.frame_counters["game"] = FrameCounter()
        # Add ClockedEvents to the frame counter.
        frame_counter = Context.timing.frame_counters["game"]
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

    @staticmethod
    def _configure_game_window() -> None:
        """Configure game window rendering."""
        renderer: Renderer = Context.renderer  # Renderer in engine/renderer.py
        renderer.window.title = "Example game"
        # Note: The window size is just an initial value.
        #   On WINDOWSIZECHANGED events, the window size and the software rendering
        #   Surface size will automatically adjust to the new size value.
        #   It is not necessary to create a new window_surface with the new window size.
        #   See handle_windowsizechanged_events.
        # renderer.window.size = (60*16, 60*9)
        # renderer.window.size = (60*16, 60*14)
        renderer.window.size = (700, 700)
        renderer.window.resizable = True
        # Additional window settings used during development:
        renderer.window.always_on_top = True
        # renderer.window.position = (950, 0)
        renderer.window.position = (0, 0)
        # renderer.window.opacity = 0.8              # This is neat
        # renderer.toggle_fullscreen()               # Start in fullscreen

    def run(self) -> None:
        """Run the game."""
        log.debug(f"Window supports OpenGL: {Context.renderer.window.opengl}")
        log.debug(f"Entities: {self.entities}")
        while True:
            self.loop()

    def loop(self) -> None:
        """Loop until the user quits."""
        # Prologue: reset debug
        Debug.hud.reset()  # Clear the debug HUD
        DebugGame.hud_begin()  # Load first values in debug HUD
        DebugGame.fps(True)
        DebugGame.window_size(True)
        # Game
        self.reset_art()  # Clear old art
        UI.consume_event_queue()  # Handle all user events
        InputMapper.ongoing_action.update(self)
        DebugGame.mouse(True)  # mouse position and buttons
        DebugGame.panning(True)  # Panning; Ctrl+Left-Click-Drag to pan
        DebugGame.player_forces(False)  # Show arrow keys: UP/DOWN/LEFT/RIGHT
        DebugGame.mode_controls(True)
        self.update_entities()
        DebugGame.entities(False)
        self.draw_remaining_art()  # Draw any remaining art not already drawn
        # Epilogue: update debug HUD, display, and timing
        self.update_frame_counters()  # Advance frame-based ticks
        DebugGame.frame_counters(True)
        Debug.display_snapshots_in_hud()  # Print snapshots in HUD last
        Context.renderer.render_all()  # Render all art and HUD
        Context.timing.maintain_framerate(fps=60)  # Run at 60 FPS

    def _subscriber_map_event_to_action(self, event: pygame.event.Event, kmod: int) -> None:
        """Map UI events to actions and then pass the action to the action handler.

        UI events include keyboard, mouse, panning, zoom, etc.
        UI is defined in 'engine/ui.py'.

        Usage:
            1. Register with the UI like this:
                UI.subscribe(self._subscriber_map_event_to_action)  # Register callback
            2. Define actions in input_mapper.py:
                - InputMapper.key_map
                - InputMapper.mouse_map
            3. Define how to handle the actions in game.py:
                - do_action_for_key_event()
                - do_action_for_mouse_button_event()
            4. Handle ongoing actions (click-dragging) in ongoing_action.py
                - OngoingAction.update(game)
            5. Game loop calls UI.consume_event_queue() which publishes all UI events
            6. Game loop calls InputMapper.ongoing_action.update(self).
               OngoingAction.update(game) checks if any ongoing actions are active and then updates
               them accordingly.

        This is a callback registered with UI. It simply maps events from the pygame event queue to
        actions and then passes the action to the action handler.

        Actions are mapped to these UI events in the InputMapper.key_map, InputMapper.mouse_map, and
        InputMapper.modifier_key_map.

        Note the key modifiers need to be filtered / cleaned up. Even with no key modifiers held
        down, kmod is 4096, not 0. I only care about ALT, CTRL, and SHIFT, so I filter the kmod
        before using it by masking it with ALT | CTRL | SHIFT.

        I use dict.get((event.key, kmod, key_direction)) to get the action corresponding to the key
        press. Unlike key_map[(event.key, kmod, key_direction)], get() does not throw an exception
        if the tuple does not exist in InputMapper.key_map. If the tuple does not exist, dict.get()
        returns None.
        """
        log.debug(f"Event: {event}")
        log.debug(f"Filtered kmod: {kmod}")
        log.debug(f"Mapped kmod: {KeyModifier.from_kmod(kmod)}")
        match event.type:
            case pygame.KEYDOWN | pygame.KEYUP:
                # Map for keydown and keyup events
                action = InputMapper.action_for_key_event(event, kmod)
                if action is not None: self.do_action_for_key_event(action)
            case pygame.MOUSEBUTTONDOWN | pygame.MOUSEBUTTONUP:
                # Map for mouse buttondown and button up events
                action = InputMapper.action_for_mouse_button_event(event, kmod)
                if action is not None: self.do_action_for_mouse_button_event(action, event.pos)

    def do_action_for_mouse_button_event(self, action: Action, position: tuple[int, int]) -> None:
        """Handle actions for mouse events detected by the UI"""
        match action:
            case Action.START_PANNING:
                log.debug("User action: start panning")
                Panning.start(position)
            case Action.STOP_PANNING:
                log.debug("User action: stop panning")
                Panning.stop(self)
            case Action.START_DRAG_PLAYER:
                log.debug("User action: start teleport player to mouse")
                InputMapper.ongoing_action.drag_player_is_active = True
            case Action.STOP_DRAG_PLAYER:
                log.debug("User action: stop teleport player to mouse")
                InputMapper.ongoing_action.drag_player_is_active = False

    # pylint: disable=too-many-statements
    # pylint: disable=too-many-branches
    def do_action_for_key_event(self, action: Action) -> None:
        """Handle actions for keyboard events detected by the UI"""
        entities = self.entities
        match action:
            case Action.QUIT:
                log.debug("User action: quit.")
                sys.exit()
            case Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK:
                log.debug("User action: clear debug snapshot artwork.")
                Debug.art.reset_snapshots()
            case Action.TOGGLE_FULLSCREEN:
                log.debug("User action: toggle fullscreen.")
                Context.renderer.toggle_fullscreen()
            case Action.TOGGLE_DEBUG_HUD:
                log.debug("User action: toggle debug HUD.")
                Debug.hud.is_visible = not Debug.hud.is_visible
            case Action.TOGGLE_PAUSE:
                log.debug("User action: toggle pause.")
                Context.timing.frame_counters["game"].toggle_pause()
                game_is_paused = Context.timing.frame_counters["game"].is_paused
                Debug.snapshots["pause"] = ("Context.timing.frame_counters['game'].is_paused: "
                                            f"{game_is_paused}")
            case Action.TOGGLE_DEBUG_ART_OVERLAY:
                log.debug("User action: toggle debug art overlay.")
                Debug.art.is_visible = not Debug.art.is_visible
            case Action.FONT_SIZE_INCREASE:
                Debug.hud.font_size.increase()
                log.debug("User action: Increase debug HUD font size."
                          f"Font size: {Debug.hud.font_size.value}.")
            case Action.FONT_SIZE_DECREASE:
                Debug.hud.font_size.decrease()
                log.debug(f"User action: Decrease debug HUD font size."
                          f"Font size: {Debug.hud.font_size.value}.")
            # TEMPORARY CODE FOR WORKING ON NPC MOTION
            case Action.CONTROLS_ADJUST_K_LESS:
                DebugGame.controls["k"] /= 2
            case Action.CONTROLS_ADJUST_K_MORE:
                DebugGame.controls["k"] *= 2
            case Action.CONTROLS_ADJUST_B_LESS:
                DebugGame.controls["b"] /= 2
            case Action.CONTROLS_ADJUST_B_MORE:
                DebugGame.controls["b"] *= 2
            # Set spring constant and damping: three modes.
            case Action.CONTROLS_PICK_MODE_1:
                log.debug("User action: Select mode 1 -- springy linked motion")
                DebugGame.mode = Mode.MODE_1
                DebugGame.controls["k"] = 0.04
                DebugGame.controls["b"] = 0.064
            case Action.CONTROLS_PICK_MODE_2:
                log.debug("User action: Select mode 2 -- rigid linked motion")
                DebugGame.mode = Mode.MODE_2
                DebugGame.controls["k"] = 1.28
                DebugGame.controls["b"] = 0.512
            case Action.CONTROLS_PICK_MODE_3:
                log.debug("User action: Select mode 3 -- separate entities following motion")
                DebugGame.mode = Mode.MODE_3
                DebugGame.controls["k"] = 0.005
                DebugGame.controls["b"] = 0.064
            case Action.PLAYER_MOVE_LEFT_GO:
                log.debug("Player move left")
                entities["player"].movement.player_force.left = True
            case Action.PLAYER_MOVE_RIGHT_GO:
                log.debug("Player move right")
                entities["player"].movement.player_force.right = True
            case Action.PLAYER_MOVE_UP_GO:
                log.debug("Player move up")
                entities["player"].movement.player_force.up = True
            case Action.PLAYER_MOVE_DOWN_GO:
                log.debug("Player move down")
                entities["player"].movement.player_force.down = True
            case Action.PLAYER_MOVE_LEFT_STOP:
                log.debug("Player move left")
                self.entities["player"].movement.player_force.left = False
            case Action.PLAYER_MOVE_RIGHT_STOP:
                log.debug("Player move right")
                self.entities["player"].movement.player_force.right = False
            case Action.PLAYER_MOVE_UP_STOP:
                log.debug("Player move up")
                self.entities["player"].movement.player_force.up = False
            case Action.PLAYER_MOVE_DOWN_STOP:
                self.entities["player"].movement.player_force.down = False
                log.debug("Player move down")
            case Action.STOP_PANNING:
                log.debug("User action: stop panning")
                Panning.stop(self)
            case Action.STOP_DRAG_PLAYER:
                log.debug("User action: stop teleport player to mouse")
                InputMapper.ongoing_action.drag_player_is_active = False

    def update_frame_counters(self) -> None:
        """Update the frame tick counters (animations are clocked by frame ticks).

        Video frames always update.
        Game frames only update if the game is not paused.
        """
        timing = Context.timing
        for frame_counter in timing.frame_counters.values():
            frame_counter.update()

    def update_entities(self) -> None:
        """Update the state of all entities based on counters and events."""
        timing = Context.timing
        for entity in self.entities.values():
            entity.update(timing)
            entity.draw()

    def reset_art(self) -> None:
        """Clear out old artwork: application and debug."""
        Art.reset()                                     # Reset application artwork
        Debug.art.reset()                          # Clear the debug artwork

    def draw_remaining_art(self) -> None:
        """Update art and debug art"""
        draw_more_stuff = False
        if draw_more_stuff:
            self.draw_background_crosses()              # Draw application artwork
            self.draw_debug_crosses()                   # Draw debug artwork

    def draw_background_crosses(self) -> None:
        """Draw some animated shapes in the background.

        Note: Framerate tanks when I zoom out too far -- zooming increases number of crosses because
        gcs_width changes. My temporary fix here is to clamp the max number of crosses, but I have a
        new problem that the origins of the crosses changes when I zoom. That is the problem with
        attempting to just draw these without any persistent state.

        LEFTOFF: These animated shapes are Entities. Now they have a persistent state! Slow
        down their animation speeds and assign different amounts of drift to each dependent on the
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
                wiggle_line = Art.randomize_line(line, wiggle)
                Art.lines.append(wiggle_line)

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
                Debug.art.lines_gcs.append(line)
