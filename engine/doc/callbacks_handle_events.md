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
actions. Even if we wanted to leave the game logic in the engine code, it is a good idea to map events to actions.

Mapping events to actions makes the action handler independent of which
specific UI event causes the action. That makes it easy to remap the UI
controls to any actions.

Since this is Python, the easiest way to do this is to define a class.
As usual, I use a `dataclass` because I just want a C-style struct that holds
my dictionary of mappings.

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

From a code readability standpoint, the constructor is a convenient place to
define the event-to-action mapping. Since this is a `dataclass`, the
`__init__()` is already defined for me, so I use the `__post_init__()`:

```python
class InputMapper:
    ...
    def __post_init__(self) -> None:
        self.key_map = {
            (pygame.K_c, pygame.KMOD_NONE): Action.CLEAR_DEBUG_SNAPSHOT_ARTWORK,
            (pygame.K_d, pygame.KMOD_NONE): Action.TOGGLE_DEBUG_ART_OVERLAY,
            (pygame.K_b, pygame.KMOD_SHIFT): Action.CONTROLS_ADJUST_B_LESS,
            (pygame.K_b, pygame.KMOD_NONE): Action.CONTROLS_ADJUST_B_MORE,
            ...
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
        ...
        key_map = self.input_mapper.key_map
        ...
        match event.type:
            case pygame.KEYDOWN:
                # Clean up kmod, then:
                action = key_map.get((event.key, kmod))
                if action is not None:
                    self._handle_action_events(action)

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

