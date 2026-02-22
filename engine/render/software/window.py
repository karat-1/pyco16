import time
import pygame
from project.projectsettings import WindowSettings


class Window:
    """
    The Window class holds all necessary information about the Pygame Window, base resolution
    scaled resolution, scale ratio, the surfaces etc. Once everything as been blitted to the display
    surface in the renderers class rendering function, the Render function from this class gets called
    and the final image is getting blitted to the screen
    """

    def __init__(self, ctx) -> None:
        """
        :param game: Game Object
        """
        self.ms = 0
        self.ctx = ctx
        self.dt = 0.1
        self.clock = pygame.time.Clock()
        self.TAGET_FPS = 60
        self.debug_dt = False
        self.tick = 0

        pygame.init()
        self.base_resolution = [
            WindowSettings.game_resolution_width,
            WindowSettings.game_resolution_height,
        ]
        self.window_resolution = [
            WindowSettings.window_width,
            WindowSettings.window_height,
        ]
        self.scale_ratio = [1, 1]
        self.offset = [0, 0]
        self.background_color = (155, 100, 114)

        self.screen = pygame.display.set_mode(self.window_resolution)
        pygame.display.set_caption("Samurai Microvania")
        pygame.mouse.set_visible(True)
        self.display = pygame.Surface(
            (
                self.base_resolution[0] - self.offset[0] * 2,
                self.base_resolution[1] - self.offset[1] * 2,
            )
        )

        self.frame_history = [0.01]
        self.frame_start = time.time()

        self.cursor_id = "cursor"
        self.freeze_frame = {}

    def render_frame(self) -> None:
        """
        This function gets called after the renderer is finished blitting the image. The display
        surface gets blitted to the screen. Also deltaTime gets calculated in here
        :return:
        """
        pygame.display.update()

        self.dt = self.clock.tick(self.tick) / 1000.0
        self.dt = max(min(self.dt, 0.1), 0.001)
        self.display.fill(self.background_color)
        pygame.display.set_caption(f"Microvania - {int(self.clock.get_fps())}fps")
