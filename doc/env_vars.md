# Setting Environment Variables

See pygame docs: [pygame](https://www.pygame.org/docs/ref/pygame.html) and find
section `Setting Environment Variables`.

## Section from docs

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

## My usage

I set the environment variables before launching Python so that I do not have
to set environment variables in code.

I use the Linux/Mac method: `ENV_VAR=value python my_application.py`.

# Put Window in Upper Right of Screen

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

# Keep Window Always On Top

*This is not an environment variable, but it is related so I am documenting it here.*

There is no way to set this through environment variables.

While it is part of SDL2, it is not part of `pygame`.

So I switched to `pygame-ce`, which provides a `Window` class where you can
access SDL2 functionality like this.

Here is the `pygame-ce` documentation for this function:
https://pyga.me/docs/ref/window.html#pygame.Window.always_on_top
