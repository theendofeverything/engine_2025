"""Top-level game code."""
import sys                  # Exit with sys.exit()
import pygame
from lib.colors import Colors
from lib.mjg_math import Vec2D, gcs_to_pcs, pcs_to_gcs


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
        self.window_surface = pygame.display.set_mode(size=(30*16, 30*9))
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

        def debug_window_size() -> str:
            # Display window size
            window_size = (30*16, 30*9)
            center = (window_size[0]/2, window_size[1]/2)
            return f"Window size: {window_size}, Center: {center} PCS\n"
        text += debug_window_size()

        def debug_mouse_position() -> str:
            # Display mouse position in pixel coordinates
            mouse_position = pygame.mouse.get_pos()
            mouse_g = pcs_to_gcs(Vec2D(x=mouse_position[0], y=mouse_position[1]))
            mouse_p = gcs_to_pcs(mouse_g)
            return f"Mouse: {(mouse_g)} GCS, {mouse_p} PCS\n"
        text += debug_mouse_position()

        def debug_fps() -> str:
            # Display frame duration in milliseconds and rate in FPS
            # # TODO: update fps every N frames instead of every frame
            # fps = 1000 / self.milliseconds_per_frame
            # # Use get_fps() for now -- it averages every 10 frames
            fps = self.clock.get_fps()
            return f"frame: {self.milliseconds_per_frame:d}ms ({fps:0.1f}FPS)"
        text += debug_fps()

        for i, line in enumerate(text.split('\n')):
            text_surface = font.render(line, True, Colors.text)
            self.window_surface.blit(
                    text_surface,
                    (pos[0], pos[1] + font.get_linesize()*i)
                    )
