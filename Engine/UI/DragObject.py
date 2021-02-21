import Engine.UI.UIElement
import Engine.GameManager
import Engine.Input
import Engine.Sprite


class DragObject(Engine.UI.UIElement.UIElement, Engine.Sprite.Sprite):
    def __init__(self, groups):
        Engine.UI.UIElement.UIElement.__init__(self)
        Engine.Sprite.Sprite.__init__(self, groups)
        self.gm = Engine.GameManager.GameManager()
        self.rel_position = [0, 0]

        self.check_interacting = self._check_interacting
        self.interact = self._interact

    def _check_interacting(self):
        if self.interacting:
            if Engine.Input.Input().get_mouse_up(1):
                self.interacting = False
        else:
            mouse_pos = Engine.Input.Input().get_screen_mouse_pos()
            if Engine.Input.Input().get_mouse_down(1):
                if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    self.rel_position[0] = self.rect[0] - mouse_pos[0]
                    self.rel_position[1] = self.rect[1] - mouse_pos[1]
                    self.interacting = True

    def _interact(self):
        mouse_pos = Engine.Input.Input().get_screen_mouse_pos()
        self.rect.x = mouse_pos[0] + self.rel_position[0]
        self.rect.y = mouse_pos[1] + self.rel_position[1]
        self.world_rect.x, self.world_rect.y = self.current_camera.screen_to_world(self.rect.x, self.rect.y)
        self.world_rect.x += self.world_rect.w // 2
        self.world_rect.y += self.world_rect.h // 2
        self.dirty = 1
