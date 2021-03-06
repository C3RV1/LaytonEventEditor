import Engine.Sprite
import Engine.GameManager
import pygame as pg


class ScreenFader(Engine.Sprite.Sprite):
    FADING_OUT = 1
    FADING_IN = 2

    def __init__(self, groups):
        super().__init__([])
        self.layer = 1000
        self.add(groups)
        self.gm = Engine.GameManager.GameManager()
        self.image = pg.Surface([256, 192])
        self.image.fill(pg.Color(0, 0, 0))
        self.image.set_alpha(0)
        self.reset_world_rect()
        self.fade = self.FADING_OUT
        self.fading = False
        self.current_time = 0
        self.fade_time = .7
        self.on_finish_fade = lambda fade_type: None
        self.run_on_finish_fade = True

        self.max_fade = 255

    def update_(self):
        if self.fading:
            self.current_time -= self.gm.delta_time
            self.update_fade()

    def finish_fade(self):
        if self.run_on_finish_fade:
            self.on_finish_fade(self.fade)

    def fade_in(self, run_fade_finish, instant_time=False):
        if self.fade == self.FADING_IN or instant_time:
            self.current_time = 0
        else:
            self.current_time = self.fade_time
        self.fade = self.FADING_IN
        self.fading = True
        self.run_on_finish_fade = run_fade_finish

    def fade_out(self, run_fade_finish, instant_time=False):
        if self.fade == self.FADING_OUT or instant_time:
            self.current_time = 0
        else:
            self.current_time = self.fade_time
        self.fade = self.FADING_OUT
        self.fading = True
        self.run_on_finish_fade = run_fade_finish

    def set_fade(self, fade, run_fade_finish):
        if self.fade == fade:
            self.current_time = 0
        else:
            self.current_time = self.fade_time
        self.fade = fade
        self.fading = True
        self.run_on_finish_fade = run_fade_finish

    def update_fade(self):
        percentage = 1 - min(max(self.current_time / self.fade_time, 0), 1)  # Clamp between 0 and 1
        if self.fade == self.FADING_OUT:
            self.image.set_alpha(int(self.max_fade * percentage))
            if self.current_time <= 0:
                self.image.set_alpha(self.max_fade)
                self.fading = False
                self.finish_fade()
        elif self.fade == self.FADING_IN:
            self.image.set_alpha(self.max_fade - int(self.max_fade * percentage))
            if self.current_time <= 0:
                self.image.set_alpha(0)
                self.fading = False
                self.finish_fade()
        else:
            self.finish_fade()
            self.fading = False
        self.dirty = 1
