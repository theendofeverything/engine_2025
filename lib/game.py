"""Top-level game code."""
import sys                  # Exit with sys.exit()
import pygame
from lib.colors import Colors
from lib.mjg_math import Point2D, Vec2D
from lib.shapes import Line2D


class Game:
    """Game data is shared by all the code"""
    clock:                  pygame.time.Clock
    milliseconds_per_frame: int
    window_size:            Vec2D
    gcs_width:              float
    window_surface:         pygame.Surface
    shapes:                 dict

    def __init__(self):
        self.setup()

    def setup(self) -> None:
        """Create the game window."""
        pygame.init()
        pygame.font.init()
        self.window_size = Vec2D(x=30*16, y=30*9)
        self.window_surface = pygame.display.set_mode(
                size=self.window_size.as_tuple(),
                flags=pygame.RESIZABLE
                )
        self.clock = pygame.time.Clock()

    def run(self, log) -> None:
        """Run the game."""
        self.milliseconds_per_frame = 16                # Initial value for debug HUD
        self.gcs_width = 2                              # GCS -1:1 fills screen width
        self.shapes = {}                                # Shape primitives
        while True:
            self.loop(log)

    def loop(self, log) -> None:
        """Loop until the user quits."""
        self.handle_events(log)

        self.draw_shapes()

        # Render
        self.window_surface.fill(Colors.background)
        self.render_shapes()
        self.render_debug_hud()
        pygame.display.flip()
        # Delay to keep game at 60 FPS.
        self.milliseconds_per_frame = self.clock.tick(60)

    def handle_events(self, log) -> None:
        """Handle events."""
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: sys.exit()
                case pygame.KEYDOWN:
                    log.debug("Keydown")
                    sys.exit()
                case pygame.WINDOWSIZECHANGED:
                    # Update window size
                    self.window_size = Vec2D(x=event.x, y=event.y)
                    log.debug(f"Event WINDOWSIZECHANGED, new size: ({event.x}, {event.y})")
                #############
                # OTHER CASES
                #############
                case pygame.MOUSEBUTTONDOWN:
                    log.debug(f"Event MOUSEBUTTONDOWN, pos: {event.pos}, button: {event.button}")
                case pygame.MOUSEBUTTONUP:
                    log.debug(f"Event MOUSEBUTTONUP, pos: {event.pos}, button: {event.button}")
                case pygame.MOUSEWHEEL:
                    match event.y:
                        case -1:
                            log.debug("ZOOM OUT")
                            self.gcs_width *= 1.1
                        case 1:
                            log.debug("ZOOM IN")
                            self.gcs_width *= 0.9
                        case _:
                            log.debug("Unexpected y-value")
                    log.debug(f"Event MOUSEWHEEL, flipped: {event.flipped}, "
                              f"x:{event.x}, y:{event.y}, "
                              f"precise_x:{event.precise_x}, precise_y:{event.precise_y}")
                case pygame.VIDEORESIZE:
                    # Do we need this?
                    log.debug(f"Event VIDEORESIZE, new size: ({event.w}, {event.h})")
                case pygame.WINDOWRESIZED:
                    # Do we need this?
                    log.debug(f"Event WINDOWRESIZED, new size: ({event.x}, {event.y})")
                case _: log.debug(event)

    def draw_shapes(self) -> None:
        """Draw shapes in GCS."""
        lines: list[Line2D] = []
        # Append line artwork to lines
        lines.append(
                Line2D(start=Point2D(-0.2, -0.2),
                       end=Point2D(0.2, 0.2)
                       ))
        lines.append(
                Line2D(start=Point2D(0.2, -0.2),
                       end=Point2D(-0.2, 0.2)
                       ))
        # Update shapes dict
        self.shapes['lines'] = lines

    def gcs_to_pcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from game coord sys to pixel coord sys."""
        # Return this
        v_p = Vec2D(x=v.x, y=v.y)
        # Flip y
        v_p.y *= -1
        # Scale based on the visible width of GCS at this zoom level
        v_p.x *= self.window_size.x/self.gcs_width
        v_p.y *= self.window_size.x/self.gcs_width
        # Translate pixel coordinate so that screen topleft maps to screen center
        # TODO: how do I want to talk about the Translation vector (pan) that
        # locates the GCS origin?
        # I need to know:
        # - the window size, (w,h), which is updated on window resize events
        # - the GCS origin, (origin_g), which is updated on zoom and pan
        translation = Vec2D(self.window_size.x/2, self.window_size.y/2)
        v_p.x += translation.x
        v_p.y += translation.y
        return v_p

    def pcs_to_gcs(self, v: Vec2D) -> Vec2D:
        """Transform vector from pixel coord sys to game coord sys."""
        # Return this
        v_g = Vec2D(x=v.x, y=v.y)
        # Translate pixel coordinate so that screen center maps to screen topleft
        translation = Vec2D(self.window_size.x/2, self.window_size.y/2)
        v_g.x -= translation.x
        v_g.y -= translation.y
        # Scale
        v_g.x *= 1/(self.window_size.x/self.gcs_width)
        v_g.y *= 1/(self.window_size.x/self.gcs_width)
        # Flip y
        v_g.y *= -1
        return v_g

    def render_shapes(self) -> None:
        """Render GCS shapes to the screen."""
        for line_g in self.shapes['lines']:
            # Convert GCS to PCS
            line_p = Line2D(start=self.gcs_to_pcs(line_g.start),
                            end=self.gcs_to_pcs(line_g.end))
            # Render to screen
            pygame.draw.line(self.window_surface,
                             Colors.line,
                             line_p.start.as_tuple(),
                             line_p.end.as_tuple()
                             )

    def render_debug_hud(self) -> None:
        """Display values in the Debug HUD."""
        font = pygame.font.SysFont("RobotoMono", 15, bold=False)
        pos = (0, 0)
        text = ""

        def debug_window_size() -> str:
            # Display window size
            center = (self.window_size.x/2, self.window_size.y/2)
            return f"Window size: {self.window_size}, Center: {center} PCS\n"
        text += debug_window_size()

        def debug_mouse_position() -> str:
            """Return string with mouse position in game and pixel coordiantes."""
            # Get mouse position in pixel coordinates
            mouse_position_tuple = pygame.mouse.get_pos()
            mouse_position = Vec2D(x=mouse_position_tuple[0],
                                   y=mouse_position_tuple[1])
            # Get mouse position in game coordinates
            mouse_g = self.pcs_to_gcs(mouse_position)
            # Test transform by converting back to pixel coordinates
            mouse_p = self.gcs_to_pcs(mouse_g)
            return ("Mouse: "
                    f"({mouse_g.x:0.1f}, {mouse_g.y:0.1f}) GCS, "
                    f"({mouse_p.x:0.1f}, {mouse_p.y:0.1f}) PCS\n"
                    )
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
