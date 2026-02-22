import time
import pygame
import moderngl
from array import array

VERTEX_SHADER = """
#version 330

in vec2 in_vert;
in vec2 in_tex;

out vec2 v_tex;

void main() {
    v_tex = in_tex;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330

uniform sampler2D tex;

in vec2 v_tex;
out vec4 f_color;

void main() {
    f_color = texture(tex, v_tex);
}
"""


class Window:
    """
    OpenGL-backed window using ModernGL.
    Keeps compatibility with existing pygame surface-based renderer
    by uploading the surface to a texture each frame.
    """

    def __init__(self, ctx=None) -> None:
        self.ms = 0
        self.dt = 0.1
        self.clock = pygame.time.Clock()
        self.debug_dt = False
        self.tick = 120
        self.ctx = ctx

        pygame.init()

        self.base_resolution = [
            self.ctx.window_settings.game_resolution_width,
            self.ctx.window_settings.game_resolution_height,
        ]

        self.window_resolution = [
            self.ctx.window_settings.window_width,
            self.ctx.window_settings.window_height,
        ]

        self.background_color =  self.ctx.window_settings.window_bg_color

        # ---- OpenGL CONTEXT ----
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK,
            pygame.GL_CONTEXT_PROFILE_CORE,
        )

        self.screen = pygame.display.set_mode(
            self.window_resolution,
            pygame.OPENGL | pygame.DOUBLEBUF
        )

        pygame.display.set_caption("Example Apps")
        pygame.mouse.set_visible(True)

        # ---- ModernGL Context ----
        self.gl_ctx = moderngl.create_context()
        self.gl_ctx.enable(moderngl.BLEND)
        self.gl_ctx.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
        )

        # ---- Shader Program ----
        self.program = self.gl_ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=FRAGMENT_SHADER,
        )

        # ---- Fullscreen Quad ----
        quad = self.gl_ctx.buffer(
            array('f', [
                # x,  y,   u,  v
                -1.0, -1.0, 0.0, 0.0,
                1.0, -1.0, 1.0, 0.0,
                -1.0, 1.0, 0.0, 1.0,
                1.0, 1.0, 1.0, 1.0,
            ])
        )

        self.vao = self.gl_ctx.simple_vertex_array(
            self.program,
            quad,
            "in_vert",
            "in_tex"
        )

        # ---- Texture matching internal resolution ----
        self.texture = self.gl_ctx.texture(
            (self.base_resolution[0], self.base_resolution[1]),
            components=4
        )

        # Pixel art filtering
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        # ---- Legacy pygame surface (temporary bridge) ----
        self.display = pygame.Surface(
            (self.base_resolution[0], self.base_resolution[1]),
            flags=pygame.SRCALPHA
        )

        self.frame_history = [0.01]
        self.frame_start = time.time()

        self.cursor_id = "cursor"
        self.freeze_frame = {}

    # --------------------------------------------------

    def render_frame(self) -> None:
        """
        Upload pygame surface to GPU texture and render fullscreen quad.
        """

        # Upload surface to GPU
        pixel_data = pygame.image.tobytes(self.display, "RGBA", True)
        self.texture.write(pixel_data)

        # Clear backbuffer
        self.gl_ctx.clear(*self.background_color)

        # Render quad
        self.texture.use(0)
        self.vao.render(moderngl.TRIANGLE_STRIP)

        # Swap buffers
        pygame.display.flip()

        # Timing
        self.dt = self.clock.tick(self.tick) / 1000.0
        self.dt = max(min(self.dt, 0.1), 0.001)

        pygame.display.set_caption(
            f"Example Apps - {int(self.clock.get_fps())}fps"
        )

        # Clear CPU surface for next frame
        self.display.fill((0, 0, 0, 0))
