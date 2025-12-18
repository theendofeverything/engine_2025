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
    game:                   "Game"
    window_surface:         pygame.Surface

    def render_all(self) -> None:
        """Called from the game loop."""
        self.window_surface.fill(Colors.background)
        self.render_shapes()
        if self.game.debug.hud.is_visible:
            self.render_debug_hud()
        pygame.display.flip()

    def render_shapes(self) -> None:
        """Render GCS shapes to the screen."""
        game = self.game

        def render_lines(lines: list[Line2D], color: pygame.Color) -> None:
            """Convert all lines from GCS to PCS and draw lines to the screen."""
            for line_g in lines:
                # Convert GCS to PCS
                line_p = Line2D(start=game.xfm.gcs_to_pcs(line_g.start.as_vec()).as_point(),
                                end=game.xfm.gcs_to_pcs(line_g.end.as_vec()).as_point()
                                )
                # Render to screen
                pygame.draw.line(self.window_surface,
                                 color,
                                 line_p.start.as_tuple(),
                                 line_p.end.as_tuple()
                                 )
        render_lines(lines=game.art.shapes["lines"], color=Colors.line)
        render_lines(lines=game.art.shapes["lines_debug"], color=Colors.line_debug)

    def render_debug_hud(self) -> None:
        """Display values in the Debug HUD."""
        game = self.game
        font = pygame.font.SysFont("RobotoMono", 15, bold=False)
        pos = (0, 0)

        def debug_window_size() -> str:
            # Display window size
            center = (game.coord_sys.window_size.x/2, game.coord_sys.window_size.y/2)
            return f"Window size: {game.coord_sys.window_size}, Center: {center} PCS"
        game.debug.hud.print(debug_window_size())

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
            return f"Mouse: {mouse_g.fmt(0.2)}, GCS, {mouse_p.fmt(0.0)}, PCS"
        game.debug.hud.print(debug_mouse_position())

        def debug_mouse_button() -> str:
            """Return string with mouse button state."""
            return ("Mouse buttons: "
                    f"1: {game.ui.mouse_button_1}"
                    )
        game.debug.hud.print(debug_mouse_button())

        def debug_pan() -> str:
            """Return string with pan values."""
            return (f"origin: {game.coord_sys.pcs_origin.fmt(0.2)}, "
                    f"translation: {game.coord_sys.translation.fmt(0.2)}\n"
                    f"Panning start: {game.ui.panning.start}, "
                    f"end: {game.ui.panning.end}, "
                    f"vector: {game.ui.panning.vector}"
                    )
        game.debug.hud.print(debug_pan())

        def debug_overlay_is_visible() -> str:
            """Return string displaying whether debug overlay is visible."""
            return f"Debug art overlay: {game.debug.art.is_visible}"
        game.debug.hud.print(debug_overlay_is_visible())

        # Print the snapshots last
        game.debug.hud.print_snapshots()

        for i, line in enumerate(game.debug.hud.text.split("\n")):
            text_surface = font.render(line, True, Colors.text)
            self.window_surface.blit(
                    text_surface,
                    (pos[0], pos[1] + font.get_linesize()*i)
                    )
