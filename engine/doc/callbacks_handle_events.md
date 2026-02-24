# UI

LEFTOFF: I made a Vim shortcut to box a visual selection. Resume making this block diagram.

```
+-------------+
| Game.loop() |
+---+---------+
    |
    |
    v
+---------------------------+
| UI.consume_event_queue()  |
+---+-----------------------+
    |
    |
    v
+-------------------------------------+
| publish(                            |
|     pygame.event.get(),             |
|     simplify(pygame.key.get_mods()) |
|     )                               |
+-------------------------------------+
```

The `UI` gets events from pygame and *publishes* them to its list of subscribers.
The list has only one subscriber, which is the callback defined by `Game`.
*Publish* simply means that `UI` calls this callback.

`UI` does not need access to `Game` to call its callback. A callback is just a
function that `Game` defines, there is no special syntax to make it a callback.
The only requirement is that its function signature matches what `UI` is
expecting. For `UI` to know about this function, `Game` loads `UI` with the
name of this function in a `UI.subscribe()` method. Now `UI` uses that name to
call the function.

`UI` is just a thin layer to separate my `Game` code from `pygame`. It is not a
complete decoupling: my `Game` code still needs to match against the
`pygame.event.Event` types. But `UI` handles iterating over the `event` queue
and it handles cleaning up the key modifiers.

I only care about three modifier keys, `Shift`, `Ctrl`, and `Alt`, and I do not
care which side modifier key (`Left` or `Right`) was pressed. I do not want to
code for all possible combinations of `Left` or `Right` modifier keys. But
`pygame` exposes this level of granularity, so to avoid lots of boilerplate
code, `UI` cleans up the key modifiers before using them in the subscriber
callback.

*Note: Everything after this is a little out of date.*

# Callbacks Handle Events

Independent of using callbacks or not, this is how the `Game` asks the engine
`UI` to handle events:

```
---------------        | ----------------------
| Game.loop() |        | | UI.handle_events() |
----+----------        | -------+--------------
    |                  |        |
    |                  |        |
    v                  |        v
----+----------------- | ============================
| UI.handle_events() | | | UI.consume_event_queue() |
---------------------- | ============================
                       |        |
                       |        |
                       |        v
                       | -------+---------------
                       | | UI.update_panning() |
                       | -----------------------
```

Besides adding callbacks, we'll also move all of the logic out to `gamelibs/`
(a module local to the game, not part of the `engine/` module). So in the end,
`UI` is just a thin glue layer between `pygame` and our game code. It will do
nothing more than take OS events and publish them to subscribers.

There are two special events that are exceptions (for now):

1. hard-quitting (developer's quick exit, not the player's quit)
2. adjusting the coordinate system after the window size changes

These could be moved out too, but as of right now I don't see a reason the
`game` needs to change how these events are handled.

## Event game logic originally defined in the engine

My engine `UI` code originally went like this.

`UI.consume_event_queue()`:

- Iterate over all events in queue
- Match on event type
- If event type == key presses:
    - Match on key press and perform game logic (quit, toggle, etc.)
- If event type == mouse:
    - Match on mouse button and perform game logic (zoom, pan)
- If event type == window:
    - Update coordinate system's window size and translate the coordinate
      system's origin by the vector from the old window center to the new
      window center

## Move event game logic into the game code

Switching to callbacks, the above diagram structure is the same, but we insert
a layer of abstraction to pull game logic out of the engine code. While we are
cleaning this up, we insert a second layer of abstraction to make it easier to
remap what UI inputs control what game logic.

The first layer of abstraction is a PubSub so that the
`UI.consume_event_queue()` does much less and leaves it up to the `Game` to
decide what the game logic is.

`UI.consume_event_queue()`:

- Iterate over all events in queue
- "Publish" each event:
    - Call every subscriber (callback) with the event and the key modifiers

The PubSub works by callbacks. To "subscribe", the Game registers callbacks
with the UI by calling a `ui.subscribe()` method which simply appends the
function name (the callback, or "subscriber") to a list of function names (the
"subscribers").

```python
class UI:
    ...
    def subscribe(self, callback: Callable[[pygame.event.Event, int], None]) -> None:
        """Call ui.subscribe(callback) to register "callback" for receiving UI events."""
        self.subscribers.append(callback)
```

To "publish", the UI iterates over the list of subscribers and calls each one
with whatever arguments it needs. In my case, there is only one subscriber:
`ui_callback_to_map_event_to_action`.

```python
class UI:
    ...
    def publish(self, event: pygame.event.Event, kmod: int) -> None:
        """Publish the event to subscribers by calling all registered callbacks."""
        for subscriber in self.subscribers:
            subscriber(event, kmod)
```

For the game to supply its own logic on what to do on these events, it registers with the UI during setup:

```python
class Game:
    ...
    def __post_init__(self) -> None:
        ...
        self.ui = UI(game=self, panning=Panning())
        self.ui.subscribe(self.ui_callback_to_map_event_to_action)
        ....
```

I mentioned above that there were two layers of abstraction. The first layer is
the PubSub we just discussed. The PubSub moves game logic from the engine code
into the game code. The second layer of abstraction is mapping events to
actions. Even if we wanted to leave the game logic in the engine code, it is a
good idea to map events to actions.

Mapping events to actions makes the action handler independent of which
specific UI event causes the action. That makes it easy to remap the UI
controls to any actions.

Since this is Python, the easiest way to do this is to define a class. As
usual, I use a `dataclass` because I just want a C-style struct that holds my
dictionaries of mappings.

I'll make a `_map` for each type of input device: `key_map` for the keyboard,
`mouse_map` for the mouse, etc. (Key modifiers are not necessarily part of
`key_map`: for example, anything like a `Ctrl+Left-Click` is part of the
`mouse_map`).

Let's just look at a `key_map` first:

```python
@dataclass
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod): Action}

    >>> input_mapper = InputMapper()
    >>> key_map = input_mapper.key_map
    >>> key_map
    {(99, 0): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
    (100, 0): <Action.TOGGLE_DEBUG_ART_OVERLAY: 3>,...
    (45, 128): <Action.FONT_SIZE_DECREASE: 8>}
    """
```

The simple `(key, keymod)` would work if I only cared about key presses. But
think about moving the player around on screen. If the user holds the move
keys, the player should keep moving until the key is released. So I need to
differentiate between key down and key up. I add a `KeyDirection` to the tuple.
This is a simple enum of `DOWN` and `UP`.

```python
class KeyDirection(Enum):
    """Enumerate names for KEYUP and KEYDOWN instead of just using bool."""
    UP = auto()
    DOWN = auto()
```

Adding `keydirection` to the tuple of our `key_map` dict key, now we can get
different actions depending on whether the key event is down (press) or up
(release).

```python
@dataclass
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod, keydirection): Action}

    >>> input_mapper = InputMapper()
    >>> key_map = input_mapper.key_map
    >>> key_map
    {(99, 0, <KeyDirection.DOWN: 2>): <Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK: 2>,
    ...
    (1073741905, 0, <KeyDirection.UP: 1>): <Action.PLAYER_MOVE_DOWN_STOP: 23>}
    """
    key_map: dict[tuple[int,  # event.key
                        int,  # kmod
                        KeyDirection  # enum
                        ],
                  Action  # enum
                  ] = field(default_factory=dict)
```

Do the same idea for a `mouse_map`. First an enum to track mouse button
direction:

```python
class ButtonDirection(Enum):
    """Enumerate names for MOUSEBUTTONUP and MOUSEBUTTONDOWN."""
    UP = auto()
    DOWN = auto()
```

Having separate `KeyDirection` and `ButtonDirection` enums are redundant, but I'm
leaving them in for now because I think having these as distinct types might
help me later.

Mouse buttons get another special enum:

```python
class MouseButton(Enum):
    """Enumerate the mouse button values from pygame.Event.button"""
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEELUP = 4
    WHEELDOWN = 5

    @classmethod
    def from_event(cls, event: pygame.Event) -> MouseButton:
        """Get MouseButton from event.button."""
        return cls(event.button)
```

Unlike the keypress events which are named after the key, `pygame` mouse button
events just identify the buttons by number. Even scrolling the mouse wheel is
assigned a number for each scroll direction, for a grand total of five button
numbers.

I use an `enum` to give these names. This eliminates the need to comment which
button is which number and it inserts a seam in my `engine` for separating
between my `engine` code and `pygame` specifics.

The `from_event()` method take the button number and gives me my enum name. I
don't need to write a `match` statement.

Here is the `InputMapper` with `key_map` and `mouse_map`:

```python
@dataclass
class InputMapper:
    """Map inputs (such as key presses) to actions.

    key_map: {(key, keymod, keydirection): Action}
    mouse_map: {(mousebutton, keymod, buttondirection): Action}

    >>> mouse_map = input_mapper.mouse_map
    >>> mouse_map
    {(<MouseButton.LEFT: 1>, 192, <ButtonDirection.DOWN: 2>): <Action.START_PANNING: 24>}
    """
    key_map: dict[tuple[int,  # event.key
                        int,  # kmod
                        KeyDirection  # enum
                        ],
                  Action  # enum
                  ] = field(default_factory=dict)
    mouse_map: dict[tuple[MouseButton,  # event.button
                          int,  # kmod
                          ButtonDirection  # enum
                          ],
                    Action  # enum
                    ] = field(default_factory=dict)
```

From a code readability standpoint, the constructor is a convenient place to
define the event-to-action mapping. Since this is a `dataclass`, the
`__init__()` is already defined for me, so I use the `__post_init__()`:

```python
class InputMapper:
    ...
    def __post_init__(self) -> None:
        no_modifier = pygame.KMOD_NONE
        shift = pygame.KMOD_SHIFT
        ctrl = pygame.KMOD_CTRL
        shift_ctrl = pygame.KMOD_SHIFT | pygame.KMOD_CTRL

        self.mouse_map = {
                (MouseButton.LEFT, ctrl, ButtonDirection.DOWN): Action.START_PANNING,
                (MouseButton.LEFT, no_modifier, ButtonDirection.UP): Action.STOP_PANNING,
                (MouseButton.LEFT, ctrl, ButtonDirection.UP): Action.STOP_PANNING,
                }

        self.key_map = {
            (pygame.K_c,      no_modifier, KeyDirection.DOWN): Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK,
            (pygame.K_d,      no_modifier, KeyDirection.DOWN): Action.TOGGLE_DEBUG_ART_OVERLAY,
            ...
            (pygame.K_DOWN,   no_modifier, KeyDirection.UP):   Action.PLAYER_MOVE_DOWN_STOP,
            }
```

The `Action` is an `Enum`:

```python
class Action(Enum):
    """Enumerate all actions for the InputMapper."""
    QUIT = auto()
    CLEAR_DEBUG_SNAPSHOT_ARTWORK = auto()
    TOGGLE_DEBUG_ART_OVERLAY = auto()
    ...
```

This `InputMapper` struct and the `Action` enum are game logic code, but they
do not have any dependence on the `Game`. The `Game` *has* an `InputMapper` and
the `Game` *has* `Actions`. There is no reason to leave these inside `game.py`.

I create a folder named `gamelibs/` and move `InputMapper` and `Action` into `gamelibs/input_mapper.py`.

To use `InputMapper` in `Game`, I register the callback
`ui_callback_to_map_event_to_action()` as already shown in the `Game` `__post_init__()` snippet above.

`ui_callback_to_map_event_to_action()`  cleans up the key modifier (see section
"Key Modifiers") and maps the UI events to an action. The action is then handed
off to an action handler.

```python
from gamelibs.input_mapper import Action, InputMapper

@dataclass
class Game:
    ...
    input_mapper: InputMapper = InputMapper()  # Map inputs to actions
    ...
    def ui_callback_to_map_event_to_action(self, event: pygame.event.Event, kmod: int) -> None:
        input_mapper = self.input_mapper
        kmod = self.ui.kmod_simplify(kmod)
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

```

And finally we have the event game logic in `_handle_action_events()`:

```python
from gamelibs.input_mapper import Action, InputMapper

@dataclass
class Game:
    ...
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
```

# Move code from UI to OngoingAction

In my initial naive pass where everything lived in the engine UI code, I had
this "player teleport" UI code that had to run *after* consuming events.

```python
    def consume_event_queue(self, log: logging.Logger) -> None:
        for event in pygame.event.get():
            ... # Handle events and set mouse.button_1 = True if button pressed
        if self.mouse.button_1:
            if kmod & pygame.KMOD_SHIFT:
                ... # Code to teleport player
```

I consumed events where I set `mouse.button_1` to be `True` or `False`. After
consuming all events, I check if I had the button held and if I had `Shift`
held. If so, I would teleport the player to the mouse position. In this way I
could `Shift` click-drag the player around.

This is a special kind of action I call an "Ongoing Action" because it
continues as long as the input is held. There are a few actions like this and
instead of spreading them all over the code, I want them to be in one place.

So I made `OngoingAction`:

```python
class OngoingAction:
    """Actions that last for multiple frames such as click-drag.

    - Panning is a Ctrl+Click-Drag
    - Teleport (or pulling on the player) is a Shift+Click-Drag

    The key modifiers and specific mouse buttons might change. But these will always be a
    click-drag. It is simpler to just query the mouse position here than to use the mouse motion
    events.
    """

    panning: Panning = Panning()
    teleport_to_mouse_is_active: bool = False

    def update(self, game: "Game") -> None:
        """Update all ongoing actions."""
        ongoing_action = self
        ongoing_action.panning.update()
        ongoing_action.teleport_to_mouse(game)

    @staticmethod
    def teleport_to_mouse(game: "Game") -> None:
        """Teleport player to mouse, like pulling on player and NPCs."""
        if game.ongoing_action.teleport_to_mouse_is_active:
            ... # Code to teleport to mouse
```

I also deleted the state variable `mouse.button_1` and made state variable
`OngoingAction.teleport_to_mouse`. I set this variable in my `UI` callback when I handle mouse action events.

```python
@dataclass
class Game:
    ...
    def ui_callback_to_map_event_to_action(self, event: pygame.event.Event, kmod: int) -> None:
        input_mapper = self.input_mapper
        kmod = self.ui.kmod_simplify(kmod)
        match event.type:
            ...
            case pygame.MOUSEBUTTONDOWN:
                mouse_button = MouseButton.from_event(event)
                ...
                action = input_mapper.key_map.get((event.key, kmod, key_direction))
                if action is not None:
                    self._handle_mouse_action_events(action, event.pos)

    def _handle_mouse_action_events(self,
                                    action: Action,
                                    position: tuple[int, int]
                                    ) -> None:
        game = self
        match action:
            ...
            case Action.START_TELEPORT_TO_MOUSE:
                log.debug("User action: start teleport player to mouse")
                game.ongoing_action.teleport_to_mouse = True
            case Action.STOP_TELEPORT_TO_MOUSE:
                log.debug("User action: stop teleport player to mouse")
                game.ongoing_action.teleport_to_mouse = False
```

# Key Modifiers

Mapping events to actions makes handling key modifiers a little more tricky.
There are two shift keys, alt keys, and control keys, each with their own key
modifier. The mapping doesn't have any way of doing a many-to-one other than
explicitly listing each of the many input key modifier combinations that all
map to the same action. This makes for a lot of redundant mapping code. There
may be an active key modifier you are not even aware of (I found `kmod` == 4096
instead of 0!).

To fix this, we first filter out any key modifiers we are not using:

```python
# Filter out irrelevant keymods
kmod = kmod & (pygame.KMOD_ALT | pygame.KMOD_CTRL | pygame.KMOD_SHIFT)
```

Then to avoid writing redundant code for all possible combinations of left and right shift/ctrl/alt, we turn any left or right key press into the combined bit flags (as if both left and right were being pressed):

```python
# Turn LSHIFT and RSHIFT into just SHIFT
if kmod & pygame.KMOD_SHIFT:
    kmod |= pygame.KMOD_SHIFT
# Turn LCTRL and RCTRL into just CTRL
if kmod & pygame.KMOD_CTRL:
    kmod |= pygame.KMOD_CTRL
# Turn LALT and RALT into just ALT
if kmod & pygame.KMOD_ALT:
    kmod |= pygame.KMOD_ALT
```

Now instead of:

```python
self.action_map = {
    ...
    (pygame.K_MINUS, pygame.KMOD_CTRL): Action.FONT_SIZE_DECREASE,
    (pygame.K_MINUS, pygame.KMOD_LCTRL): Action.FONT_SIZE_DECREASE,
    (pygame.K_MINUS, pygame.KMOD_RCTRL): Action.FONT_SIZE_DECREASE,
    ...
```

We just have:

```python
self.action_map = {
    ...
    (pygame.K_MINUS, pygame.KMOD_CTRL): Action.FONT_SIZE_DECREASE,
    ...
```

