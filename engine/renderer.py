"""Renderer holds all game rendering code.
"""
from dataclasses import dataclass, field
import pygame
from .drawing_shapes import Line2D
from .colors import Colors


@dataclass
class Renderer:
    """Renderer."""
    game:                   "Game"
    window:                 pygame.Window = pygame.Window()
    window_surface:         pygame.Surface = field(init=False)
    is_fullscreen:          bool = False

    def __post_init__(self) -> None:
        # NOTE: from pygame-ce docs:
        # Don't use window.get_surface() when using hardware rendering
        self.window_surface = self.window.get_surface()

    def toggle_fullscreen(self) -> None:
        """Toggle between windowed mode and fullscreen."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.window.set_fullscreen(desktop=True)
        else:
            self.window.set_windowed()

    def render_all(self) -> None:
        """Called from the game loop."""
        game = self.game
        self.window_surface.fill(Colors.background)
        self.render_shapes()
        if game.debug.hud.is_visible:
            self.render_debug_hud()
        self.window.flip()

    def render_shapes(self) -> None:
        """Render GCS shapes to the screen."""
        game = self.game

        def render_line_to_screen(line: Line2D) -> None:
            """Render a line in PCS to the screen."""
            # Render to screen
            pygame.draw.line(self.window_surface,
                             line.color,
                             line.start.as_tuple(),
                             line.end.as_tuple()
                             )

        def render_gcs_lines(lines: list[Line2D]) -> None:
            """Convert all lines from GCS to PCS and draw lines to the screen."""
            for line_g in lines:
                # Convert GCS to PCS
                xfm = game.coord_sys.matrix.gcs_to_pcs
                line_p = Line2D(start=game.coord_sys.xfm(line_g.start.as_vec(), xfm).as_point(),
                                end=game.coord_sys.xfm(line_g.end.as_vec(), xfm).as_point(),
                                color=line_g.color)
                render_line_to_screen(line_p)

        def render_pcs_lines(lines: list[Line2D]) -> None:
            """Draw PCS lines to the screen."""
            for line_p in lines:
                render_line_to_screen(line_p)

        render_gcs_lines(lines=game.art.lines)
        if game.debug.art.is_visible:
            render_gcs_lines(lines=game.debug.art.lines_gcs)
            render_pcs_lines(lines=game.debug.art.lines_pcs)
            render_gcs_lines(lines=game.debug.art.snapshots)

    def render_debug_hud(self) -> None:
        """Display values in the Debug HUD."""
        game = self.game
        font = pygame.font.Font(game.debug_font, game.debug.hud.font_size.value)
        pos = (0, 0)

        # Iterate over lines of debug HUD text using debug.hud.lines.
        # Generate a texture for each line and blit that texture to the OS window.
        for i, line in enumerate(game.debug.hud.lines):
            text_surface = font.render(line, True, Colors.text)
            self.window_surface.blit(
                    text_surface,
                    (pos[0], pos[1] + font.get_linesize()*i)
                    )
