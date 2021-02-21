import Engine.UI.UIElement
import Engine.Input
import Engine.Sprite


class Button(Engine.UI.UIElement.UIElement, Engine.Sprite.Sprite):
    def __init__(self, groups):
        super(Button, self).__init__()
        Engine.Sprite.Sprite.__init__(self, groups)
        self.command = None

        self.check_interacting = self._check_interacting
        self.interact = self._interact

    def _check_interacting(self):
        mouse_pos = Engine.Input.Input().get_screen_mouse_pos()
        if Engine.Input.Input().get_mouse_down(1):
            if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                self.interacting = True
                return
        self.interacting = False

    def _interact(self):
        if callable(self.command):
            self.command()
