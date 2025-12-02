#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :
"""Game kata 2025-11-17

* [x] Fill the screen with a color
    * This required that I:
        * store the Surface returned by pygame.display.set_mode in the Game
        * pass the Game to loop()
* [x] Draw something on the screen
    * I drew a line using pygame.draw.line()
* [x] Replace pygame.color.Color() with named colors:
    * Create a library of named colors: Colors.name1, Colors.name2, etc.
* [x] Render some text
* [x] Render mouse position
    [x] Create shortcut ;kpg to open local copy of pygame docs in browser
* [x] Render FPS and milliseconds per frame
* [ ] Replace pixel coordinates with world space coordinates
    * Create a transform to map from world space to pixel space
"""
import atexit               # Register a function to run on exit
from pathlib import Path    # Get file paths
import pygame
from lib.log import setup_logging
from lib.game import Game


def shutdown(file: str, log) -> None:
    """Safe shutdown on exit, such as sys.exit()."""
    log.debug("Shutdown %s", Path(file).name)
    pygame.font.quit()
    pygame.quit()
    log.debug("Shutdown finished.")


if __name__ == '__main__':
    _log = setup_logging()
    _log.debug("Run %s", Path(__file__).name)
    atexit.register(shutdown, __file__, _log)
    Game().run(_log)
