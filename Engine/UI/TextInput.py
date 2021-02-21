import Engine.UI.UIElement
import Engine.UI.Text
import Engine.Input
import pygame as pg
import Engine.Camera
import re


class TextInput(Engine.UI.UIElement.UIElement, Engine.UI.Text.Text):
    def __init__(self, groups, default_text="Enter text..."):
        super(TextInput, self).__init__()
        Engine.UI.Text.Text.__init__(self, groups)
        self.value = ""
        self.valid_regex = None

        self.check_interacting = self._check_interacting
        self.interact = self._interact

        self.default_text = default_text

    def update_display_text(self):
        if self.value == "":
            self.set_text(self.default_text)
        else:
            self.set_text(self.value)
        self.world_rect[2] = self.image.get_rect().w
        self.world_rect[3] = self.image.get_rect().h
        self.dirty = 1

    def set_font(self, font_path, size):
        Engine.UI.Text.Text.set_font(self, font_path, size)
        self.update_display_text()

    def _check_interacting(self):
        mouse_pos = Engine.Input.Input().get_screen_mouse_pos()
        if not self.interacting:
            if Engine.Input.Input().get_mouse_down(1):
                if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    self.interacting = True
        else:
            if Engine.Input.Input().get_mouse_down(1):
                if not self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    self.interacting = False

    def _interact(self):
        Engine.Input.Input().grab_key_input()
        for event in Engine.Input.Input().last_events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.interacting = False
                    continue
                elif event.key == pg.K_BACKSPACE:
                    self.value = self.value[:-1]
                else:
                    pre_value = self.value
                    self.value += event.unicode
                    if self.valid_regex is not None:
                        if not re.match(self.valid_regex, self.value):
                            self.value = pre_value
                self.update_display_text()
