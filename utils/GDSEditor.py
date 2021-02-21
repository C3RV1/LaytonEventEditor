import Engine.Camera
from Engine import Renderer
import pygame as pg


class GDSEditor(Renderer.Renderer):
    def __init__(self):
        super(GDSEditor, self).__init__()

        self.group = pg.sprite.LayeredDirty()
        self.camera = Engine.Camera.Camera()
        self.camera.display_port = pg.Rect(256*3, 192 * 2, 1280 - 256 * 3, 192 * 2)
        self.group.set_clip(self.camera.display_port)

        self.blank_surface.fill(pg.Color(40, 40, 40))

    def clear(self):
        self.group.clear(self.screen, self.blank_surface)

    def update(self):
        pass

    def draw(self):
        self.camera.draw(self.group)
        dirty = self.group.draw(self.screen)
        return dirty
