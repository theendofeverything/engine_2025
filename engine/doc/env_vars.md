# Setting Environment Variables

See pygame docs: [pygame](https://www.pygame.org/docs/ref/pygame.html) and find
section `Setting Environment Variables`.

Note: after switching from `pygame` to `pygame-ce`, I do not need to touch
environment variables to get the desired window behavior.

## Section from pygame docs

> In python, environment variables are usually set in code like this:

```python
import os
os.environ['NAME_OF_ENVIRONMENT_VARIABLE'] = 'value_to_set'
```

> Or to preserve users ability to override the variable:

```python
import os
os.environ['ENV_VAR'] = os.environ.get('ENV_VAR', 'value')
```

> If the variable is more useful for users of an app to set than the developer then they can set it like this:
>
> Windows:

```
set NAME_OF_ENVIRONMENT_VARIABLE=value_to_set
python my_application.py
```

> Linux/Mac:

```
ENV_VAR=value python my_application.py
```

# My usage of env vars

## pygame

I set the environment variables before launching Python so that I do not have
to set environment variables in code.

I use the Linux/Mac method: `ENV_VAR=value python my_application.py`.

## pygame-ce

I do not set any environment variables.

# Get a window from the OS

## pygame

When I instantiate the `Renderer`, I make a window and set some values. The
values that are only configurable as environment variables are handled by the
Makefile recipe.

```python
class Game:
    def __post_init__() -> None:
        ...
        self.renderer = Renderer(
                game=self,
                window_surface=pygame.display.set_mode(  # Get a window from the OS
                    size=window_size,
                    flags=pygame.RESIZABLE
                    ))
        ...

@dataclass
class Renderer:
    game:                   "Game"
    window_surface:         pygame.Surface
```

## pygame-ce

I define `Game` and `Renderer` slightly differently, taking advantage of the
pygame-ce `pygame.Window` class.

The `__post_init__()` of my `Renderer` class makes a `pygame.Window`. So when
`Game` makes a `Renderer`, I have a `self.game.renderer.window`. I do all
configuration in `Game` after the window is created. This gives a lot more
control over window behavior, all of which is definable in `game.py`.

```python
class Game:
    def __post_init__(self) -> None:
    ...
        self.renderer = Renderer(game=self)
        self.renderer.window.title = "Example game"
        self.renderer.window.size = (60*16, 60*9)
        self.renderer.window.resizable = True
```

# Put Window in Upper Right of Screen

## pygame

My `Makefile` use to define `make run` like this:

```make
run:
	./main.py`
```

During development, I want the window to open in the upper right of my screen
so that it does not block my text editor. So I modified the `run` recipe:

```make
run:
	SDL_VIDEO_WINDOW_POS="950,0" ./main.py
```

## pygame-ce

After creating the `renderer`, I can set the window position (any time I
choose) like this:

```python
        self.renderer.window.position = (950, 0)
```

I do this in `Game` instead of `Renderer` so that this is project-specific, not
hard-coded into the engine.

# Keep Window Always On Top

## pygame

*This is not an environment variable, but it is related so I am documenting it here.*

There is no way to set this through environment variables. While it is part of
SDL2, it is not part of `pygame`.

So I switched to `pygame-ce`, which provides a `Window` class where you can
access SDL2 functionality like this.

## pygame-ce

Here is the `pygame-ce` documentation for this function:
https://pyga.me/docs/ref/window.html#pygame.Window.always_on_top

The following works for me on Ubuntu:

```
        self.renderer.window.always_on_top = True
```
