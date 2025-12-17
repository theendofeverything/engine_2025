"""Renderer holds all game rendering code.
"""
from dataclasses import dataclass
import pygame
from .drawing_shapes import Line2D
from .geometry_types import Vec2D
from .colors import Colors


@dataclass
class Renderer:
    """Renderer."""
    game:                   'Game'
    window_surface:         pygame.Surface

    def render_all(self) -> None:
        """Called from the game loop."""
        self.window_surface.fill(Colors.background)
        self.render_shapes()
        self.render_debug_hud()
        pygame.display.flip()

    def render_shapes(self) -> None:
        """Render GCS shapes to the screen."""
        game = self.game
        # Convert all lines from GCS to PCS and draw lines to the screen.
        for line_g in game.shapes['lines']:
            # Convert GCS to PCS
            line_p = Line2D(start=game.xfm.gcs_to_pcs(line_g.start.as_vec()).as_point(),
                            end=game.xfm.gcs_to_pcs(line_g.end.as_vec()).as_point()
                            )
            # Render to screen
            pygame.draw.line(self.window_surface,
                             Colors.line,
                             line_p.start.as_tuple(),
                             line_p.end.as_tuple()
                             )

    def render_debug_hud(self) -> None:
        """Display values in the Debug HUD."""
        game = self.game
        font = pygame.font.SysFont("RobotoMono", 15, bold=False)
        pos = (0, 0)
        text = ""

        def debug_window_size() -> str:
            # Display window size
            center = (game.coord_sys.window_size.x/2, game.coord_sys.window_size.y/2)
            return f"Window size: {game.coord_sys.window_size}, Center: {center} PCS\n"
        text += debug_window_size()

        def debug_mouse_position() -> str:
            """Return string with mouse position in game and pixel coordiantes."""
            # Get mouse position in pixel coordinates
            mouse_position_tuple = pygame.mouse.get_pos()
            mouse_position = Vec2D(x=mouse_position_tuple[0],
                                   y=mouse_position_tuple[1])
            # Get mouse position in game coordinates
            mouse_g = game.xfm.pcs_to_gcs(mouse_position)
            # Test transform by converting back to pixel coordinates
            mouse_p = game.xfm.gcs_to_pcs(mouse_g)
            return ("Mouse: "
                    f"({mouse_g.x:0.1f}, {mouse_g.y:0.1f}) GCS, "
                    f"({mouse_p.x:0.1f}, {mouse_p.y:0.1f}) PCS\n"
                    )
        text += debug_mouse_position()

        def debug_mouse_button() -> str:
            """Return string with mouse button state."""
            return ("Mouse buttons: "
                    f"1: {game.ui.mouse_button_1}\n"
                    )
        text += debug_mouse_button()

        def debug_pan() -> str:
            """Return string with pan values."""
            return (f"origin: {game.coord_sys.pcs_origin}, "
                    f"translation: {game.coord_sys.translation}\n"
                    f"pan_start: {game.ui.panning.start}, "
                    f"pan_end: {game.ui.panning.end}\n"
                    )
        text += debug_pan()

        def debug_fps() -> str:
            # Display frame duration in milliseconds and rate in FPS
            # # TODO: update fps every N frames instead of every frame
            # fps = 1000 / self.timing.ms_per_frame
            # # Use get_fps() for now -- it averages every 10 frames
            fps = game.timing.clock.get_fps()
            return f"frame: {game.timing.ms_per_frame:d}ms ({fps:0.1f}FPS)"
        text += debug_fps()

        for i, line in enumerate(text.split('\n')):
            text_surface = font.render(line, True, Colors.text)
            self.window_surface.blit(
                    text_surface,
                    (pos[0], pos[1] + font.get_linesize()*i)
                    )
