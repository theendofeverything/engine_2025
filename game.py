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
from engine.panning import Panning
from engine.coord_sys import CoordinateSystem
from engine.renderer import Renderer
from engine.geometry_types import Point2D, Vec2D
from engine.drawing_shapes import Cross
from engine.colors import Colors
from engine.entity import Entity, EntityType
from gamelibs.input_mapper import Action, InputMapper, KeyDirection
from gamelibs.input_mapper import MouseButton, ButtonDirection
from gamelibs.debug_game import DebugGame, Mode

FILE = pathlib.Path(__file__).name


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
         debug=Debug(...),
         timing=Timing(...),
         art=Art(...),
         renderer=Renderer(...),
         ui=UI(...),
         coord_sys=CoordinateSystem(...),
         entities={...},
         input_mapper=InputMapper(...))
    """
    ###################################
    # Engine-defined instance variables
    ###################################
    # Instance variables defined in the implicit __init__() of dataclass
    log:        logging.Logger  # log created in main.py
    debug:      Debug = Debug()     # Display debug prints in HUD and overlay debug art
    timing:     Timing = Timing()   # Set up a clock to set frame rate and measure frame period
    art:        Art = Art()         # Set up all artwork for rendering
    # Instance variables defined in __post_init__()
    renderer:   Renderer = field(init=False)
    ui:         UI = field(init=False)                      # Keyboard, mouse, panning, zoom
    coord_sys:  CoordinateSystem = field(init=False)        # Track state of PCS and GCS
    entities:   dict[str, Entity] = field(init=False)   # Game characters like the player

    #################################
    # Game-defined instance variables
    #################################
    # Instance variables defined in the implicit __init__() of dataclass
    input_mapper: InputMapper = InputMapper()  # Map inputs to actions
    # Instance variables defined in __post_init__()
    debug_game: DebugGame = field(init=False)

    def __post_init__(self) -> None:
        # Load pygame
        pygame.init()
        pygame.font.init()
        self.debug_font = "fonts/ProggyClean.ttf"
        self.debug_game = DebugGame(game=self)

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
                debug_game=self.debug_game,
                entities=self.entities,
                entity_type=EntityType.PLAYER,
                clocked_event_name="period_3",
                # origin=Point2D(0.5, 0),
                )
        self.entities["cross1"] = Entity(
                debug=self.debug,
                debug_game=self.debug_game,
                entities=self.entities,
                entity_type=EntityType.NPC,
                clocked_event_name="period_3",
                # clocked_event_name="period_1",
                # origin=Point2D(0, 0.25),
                )
        self.entities["cross2"] = Entity(
                debug=self.debug,
                debug_game=self.debug_game,
                entities=self.entities,
                entity_type=EntityType.NPC,
                clocked_event_name="period_3",
                size=0.15,
                # clocked_event_name="period_1",
                # origin=Point2D(0, -0.5),
                )
        # Create entities for background art
        # 5 x 5 grid of crosses named "bgnd1" ... "bgnd10"
        size = 0.07
        num_crosses_x = 13
        num_crosses_y = 13
        dist = Vec2D(x=2*size, y=2*size)
        coord_sys = self.coord_sys
        start = Point2D(x=-1*coord_sys.gcs_width/2 + 0.1,
                        y=-1*coord_sys.gcs_width/2 + 0.1)
        for i in range(num_crosses_x):
            for j in range(num_crosses_y):
                number = 1 + j + (i*num_crosses_x)
                name = f"bgnd{number}"
                self.entities[name] = Entity(
                        debug=self.debug,
                        debug_game=self.debug_game,
                        entities=self.entities,
                        entity_type=EntityType.BACKGROUND_ART,
                        size=size,
                        origin=Point2D(start.x + i*dist.x,
                                       start.y + j*dist.y),
                        )
                me = self.entities[name]
                # Respond to the player
                me.movement.follow_entities = ["player", "cross1", "cross2"]
                # Be excited in general
                me.amount_excited.low *= 2
                # Get very excited when player is near
                me.amount_excited.high *= 2
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
        self.debug_game.hud_begin()                          # Load first values in debug HUD
        self.debug_game.fps(True)
        self.debug_game.window_size(True)
        # Game
        self.reset_art()                                # Clear old art
        self.ui.handle_events(log)                      # Handle all user events
        self.debug_game.mouse(False)  # Mouse position and buttons
        self.debug_game.panning(True)  # Panning; Ctrl+Left-Click-Drag to pan
        self.debug_game.player_forces(False)  # Show arrow keys: UP/DOWN/LEFT/RIGHT
        self.debug_game.mode_controls(True)
        self.update_entities()
        self.debug_game.entities(False)
        self.draw_remaining_art()                       # Draw any remaining art not already drawn
        # Epilogue: update debug HUD, display, and timing
        self.update_frame_counters()                    # Advance frame-based ticks
        self.debug_game.frame_counters(True)
        self.debug.display_snapshots_in_hud()           # Print snapshots in HUD last
        self.renderer.render_all()                      # Render all art and HUD
        self.timing.maintain_framerate(fps=60)          # Run at 60 FPS

    def ui_callback_to_map_event_to_action(self, event: pygame.event.Event, kmod: int) -> None:
        """Map UI events to actions and then pass the action to the action handler.

        Usage:
            1. Register with the UI like this:
                self.ui = UI(game=self, ...)  # Instantiate UI
                self.ui.subscribe(self.ui_callback_to_map_event_to_action)  # Register callback
            2. Define actions in the InputMapper.key_map
            3. Define how to handle the actions in _handle_keyboard_action_events()

        This is a callback registered with UI. It simply maps events from the pygame event queue to
        actions and then passes the action to the action handler.

        Actions are defined in the InputMapper.key_map:
            {(99, 0, <KeyDirection.DOWN: 2>): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
            (100, 0, <KeyDirection.DOWN: 2>): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,
            (98, 3, <KeyDirection.DOWN: 2>): <Action.CONTROLS_ADJUST_B_LESS: 11>,
            ...

            The dictionary key (int, int, KeyDirection) is the tuple (event.key, kmod, KeyDirection)
            where:
                - event.key is the int key code of the key press
                - kmod is the int of the bitfield representing which key modifiers are held,
                  returned by pygame.key.get_mods()
                - KeyDirection is KeyDirection.DOWN (for a pygame.KEYDOWN event) or KeyDirection.UP
                  (for a pygame.KEYUP event)

        Even with no key modifiers held down, kmod is 4096, not 0. I only care about ALT, CTRL, and
        SHIFT, so I filter the kmod before using it by masking it with ALT | CTRL | SHIFT.

        I use dict.get((event.key, kmod, key_direction)) to get the action corresponding to the key
        press. Unlike key_map[(event.key, kmod, key_direction)], get() does not throw an exception
        if the tuple does not exist in InputMapper.key_map. If the tuple does not exist, dict.get()
        returns None.
        """
        input_mapper = self.input_mapper
        log = self.log
        kmod = self.ui.kmod_simplify(kmod)
        log.debug(f"Event: {event}")
        log.debug(f"Filtered kmod: {kmod}")
        match event.type:
            case pygame.KEYDOWN | pygame.KEYUP:
                # Get the keydirection
                match event.type:
                    case pygame.KEYDOWN:
                        log.debug("KEYDOWN")
                        key_direction = KeyDirection.DOWN
                    case pygame.KEYUP:
                        log.debug("KEYUP")
                        key_direction = KeyDirection.UP
                action = input_mapper.key_map.get((event.key, kmod, key_direction))
                if action is not None:
                    self._handle_keyboard_action_events(action)
            case pygame.MOUSEBUTTONDOWN:
                log.debug("Event MOUSEBUTTONDOWN, "
                          f"pos: {event.pos}, ({type(event.pos[0])}), "
                          f"event.button: {event.button}, "
                          f"MouseButton: {MouseButton.from_event(event)}")
                # NEXT: add the action for the middle button press
                match event.button:
                    case 1:
                        self.ui.mouse.button_1 = True
                        mouse_button = MouseButton.LEFT
                    case 2:
                        self.ui.mouse.button_2 = True
                        mouse_button = MouseButton.MIDDLE
                    case 2:
                        self.ui.mouse.button_3 = True
                        mouse_button = MouseButton.RIGHT
                    case 4:
                        # Unused -- should this even be here?
                        mouse_button = MouseButton.WHEELUP
                    case 5:
                        # Unused -- should this even be here?
                        mouse_button = MouseButton.WHEELDOWN
                    case _:
                        mouse_button = MouseButton.UNKNOWN

                button_direction = ButtonDirection.DOWN
                action = input_mapper.mouse_map.get(
                        (mouse_button, kmod, button_direction))
                log.debug(f"BOB ACTION: {action}")
                log.debug(f"event.button: {event.button}")
                log.debug(f"kmod: {kmod}")
                log.debug(f"button_direction: {button_direction}")
                if action is not None:
                    self._handle_mouse_action_events(action, event.pos)

    def _handle_mouse_action_events(self,
                                    action: Action,
                                    position: tuple[int, int]
                                    ) -> None:
        """Handle mouse action events detected by the UI"""
        log = self.log
        game = self
        match action:
            case Action.START_PANNING:
                log.debug("User action: start panning")
                game.ui.start_panning(position)

    # pylint: disable=too-many-statements
    # pylint: disable=too-many-branches
    def _handle_keyboard_action_events(self, action: Action) -> None:
        """Handle keyboard actions events detected by the UI"""
        log = self.log
        game = self
        entities = self.entities
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
                game.debug_game.controls["k"] /= 2
            case Action.CONTROLS_ADJUST_K_MORE:
                game.debug_game.controls["k"] *= 2
            case Action.CONTROLS_ADJUST_B_LESS:
                game.debug_game.controls["b"] /= 2
            case Action.CONTROLS_ADJUST_B_MORE:
                game.debug_game.controls["b"] *= 2
            # Set spring constant and damping: three modes.
            case Action.CONTROLS_PICK_MODE_1:
                log.debug("User action: Select mode 1 -- springy linked motion")
                game.debug_game.mode = Mode.MODE_1
                game.debug_game.controls["k"] = 0.04
                game.debug_game.controls["b"] = 0.064
            case Action.CONTROLS_PICK_MODE_2:
                log.debug("User action: Select mode 2 -- rigid linked motion")
                game.debug_game.mode = Mode.MODE_2
                game.debug_game.controls["k"] = 1.28
                game.debug_game.controls["b"] = 0.512
            case Action.CONTROLS_PICK_MODE_3:
                log.debug("User action: Select mode 3 -- separate entities following motion")
                game.debug_game.mode = Mode.MODE_3
                game.debug_game.controls["k"] = 0.005
                game.debug_game.controls["b"] = 0.064
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

    def update_frame_counters(self) -> None:
        """Update the frame tick counters (animations are clocked by frame ticks).

        Video frames always update.
        Game frames only update if the game is not paused.
        """
        timing = self.timing
        for frame_counter in timing.frame_counters.values():
            frame_counter.update()

    def update_entities(self) -> None:
        """Update the state of all entities based on counters and events."""
        timing = self.timing
        art = self.art
        for entity in self.entities.values():
            entity.update(timing)
            entity.draw(art)

    def reset_art(self) -> None:
        """Clear out old artwork: application and debug."""
        self.art.reset()                                # Reset application artwork
        self.debug.art.reset()                          # Clear the debug artwork

    def draw_remaining_art(self) -> None:
        """Update art and debug art"""
        draw_more_stuff = False
        if draw_more_stuff:
            self.draw_background_crosses()              # Draw application artwork
            self.draw_debug_crosses()                   # Draw debug artwork

    # TODO: THIS IS NOT USED ANYMORE -- MOVE IT OUT AFTER ADDRESSING TODO BELOW
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
