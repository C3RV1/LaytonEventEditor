import Engine.GameManager
import pygame as pg
import Engine.Sprite
import Engine.Camera
import Engine.Input
import Engine.Screen
import Engine.Animation


class Renderer:
    def __init__(self):
        self.gm = Engine.GameManager.GameManager()
        self.screen = Engine.Screen.Screen.screen()
        self.screen_size = Engine.Screen.Screen.screen_size()
        self.inp = Engine.Input.Input()

        self.blank_surface = pg.Surface(Engine.Screen.Screen.screen_size())
        self.blank_surface.fill(pg.Color(40, 40, 40))

        self.running = True
        self.first_clear = False

    def run(self):
        dirties = []
        self.clear()
        self.update()
        dirties.extend(self.draw())
        dirties.extend(self.post_draw())
        return dirties

    def exit(self):
        self.gm.exit()

    def clear(self):
        pass

    def fill(self):
        pass

    def update(self):
        return []

    def draw(self):
        return []

    def post_draw(self):
        return []

    def load(self):
        pass

    def unload(self):
        pass
