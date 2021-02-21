import Engine.Camera
import Engine.UI.UIElement
import Engine.Input


class DraggableCamera(Engine.Camera.Camera, Engine.UI.UIElement.UIElement):
    def __init__(self):
        self.inp = Engine.Input.Input()
        Engine.Camera.Camera.__init__(self)
        Engine.UI.UIElement.UIElement.__init__(self)
        self.rel_position = [0, 0]

        self.check_interacting = self.check_interact_
        self.interact = self.interact_

    def check_interact_(self):
        if not self.interacting:
            mouse_pos = self.inp.get_screen_mouse_pos()
            if self.inp.get_mouse_down(1) and self.display_port.collidepoint(mouse_pos):
                self.rel_position[0] = self.position[0] - mouse_pos[0]
                self.rel_position[1] = self.position[1] - mouse_pos[1]
                self.interacting = True
                self.interacting = True
        else:
            if self.inp.get_mouse_up(1):
                self.interacting = False

    def interact_(self):
        mouse_pos = Engine.Input.Input().get_screen_mouse_pos()
        self.position[0] = mouse_pos[0] + self.rel_position[0]
        self.position[1] = mouse_pos[1] + self.rel_position[1]