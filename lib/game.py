"""Top-level game code."""
import sys                  # Exit with sys.exit()
import pygame
from lib.colors import Colors


class Game:
    """Game data is shared by all the code"""
    def __init__(self):
        self.clock = None
        self.window_surface = None
        self.setup()

    def setup(self) -> None:
        """Create the game window."""
        pygame.init()
        self.window_surface = pygame.display.set_mode(size=(20*16, 20*9))
        self.clock = pygame.time.Clock()

    def run(self, log) -> None:
        """Run the game."""
        while True:
            self.loop(log)

    def loop(self, log) -> None:
        """Loop until the user quits."""
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: sys.exit()
                case pygame.KEYDOWN:
                    log.debug("Keydown")
                    sys.exit()
                case _: log.debug(event)
        self.window_surface.fill(Colors.background)
        pygame.draw.line(self.window_surface,
                         Colors.line,
                         (20, 20),
                         (60, 60))
        pygame.display.flip()
        self.clock.tick(60)
