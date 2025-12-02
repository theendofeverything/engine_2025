"""Top-level game code."""
import sys                  # Exit with sys.exit()
import pygame
from lib.colors import Colors


class Game:
    """Game data is shared by all the code"""
    def __init__(self):
        self.clock = None
        self.milliseconds_per_frame = 16
        self.window_surface = None
        self.setup()

    def setup(self) -> None:
        """Create the game window."""
        pygame.init()
        pygame.font.init()
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

        # Render
        self.window_surface.fill(Colors.background)
        pygame.draw.line(self.window_surface,
                         Colors.line,
                         (20, 20),
                         (60, 60))
        self.render_debug_hud()
        pygame.display.flip()
        # Delay to keep game at 60 FPS.
        self.milliseconds_per_frame = self.clock.tick(60)

    def render_debug_hud(self) -> None:
        """Display values in the Debug HUD."""
        font = pygame.font.SysFont("RobotoMono", 15, bold=False)
        pos = (0, 0)
        text = ""
        # Display mouse position in pixel coordinates
        mouse_position = pygame.mouse.get_pos()
        text += f"Mouse: {mouse_position}\n"
        # Display frame duration in milliseconds and rate in FPS
        # # TODO: update fps every N frames instead of every frame
        # fps = 1000 / self.milliseconds_per_frame
        # # Use get_fps() for now -- it averages every 10 frames
        fps = self.clock.get_fps()
        text += f"frame: {self.milliseconds_per_frame:d}ms ({fps:0.1f}FPS)"
        for i, line in enumerate(text.split('\n')):
            text_surface = font.render(line, True, Colors.text)
            self.window_surface.blit(
                    text_surface,
                    (pos[0], pos[1] + font.get_linesize()*i)
                    )
