from pyglet import gl
import pyglet.graphics
from pyglet.window import Window


class SurfaceRenderer(object):
    def __init__(self, surface):
        self.surface = surface
        self.win = Window(width=640, height=480)
        self.win.on_draw(self.draw)

        vertices = pyglet.graphics.vertex_list() 

    def draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


