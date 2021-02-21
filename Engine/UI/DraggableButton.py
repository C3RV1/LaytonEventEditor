import Engine.UI.UIElement
import Engine.Input
import Engine.GameManager
import Engine.Sprite


class DraggableButton(Engine.UI.UIElement.UIElement, Engine.Sprite.Sprite):
    def __init__(self, groups):
        super(DraggableButton, self).__init__()
        Engine.Sprite.Sprite.__init__(self, groups)

        self.mouse_start_pos = [0, 0]
        self.mouse_drag_distance = 10 ** 2
        self.rel_position = [0, 0]

        self.press_command = None

        self.dragging = False

        self.check_interacting = self._check_interacting
        self.interact = self._interact

    def _check_interacting(self):
        if not self.interacting:
            mouse_pos = Engine.Input.Input().get_screen_mouse_pos()
            if Engine.Input.Input().get_mouse_down(1):
                if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    self.interacting = True
                    self.rel_position[0] = self.world_rect[0] - mouse_pos[0]
                    self.rel_position[1] = self.world_rect[1] - mouse_pos[1]
                    self.mouse_start_pos = mouse_pos
                    self.dragging = False
        else:
            if Engine.Input.Input().get_mouse_up(1):
                if not self.dragging:
                    if callable(self.press_command):
                        self.press_command()
                self.interacting = False

    def _interact(self):
        mouse_pos = Engine.Input.Input().get_screen_mouse_pos()
        if self.dragging:
            self.world_rect.x = mouse_pos[0] + self.rel_position[0]
            self.world_rect.y = mouse_pos[1] + self.rel_position[1]
            self.dirty = 1
        else:
            distance = (self.mouse_start_pos[0] - mouse_pos[0]) ** 2 + (self.mouse_start_pos[1] - mouse_pos[1]) ** 2
            if distance > self.mouse_drag_distance:
                self.dragging = True

    def stick_to(self, point):
        self.world_rect[0] = point[0]
        self.world_rect[1] = point[1]
        self.dirty = 1

    def stick_closest(self, points):
        closest = []
        closest_d = -1

        for point in points:
            point_diff = [point[0], point[1]]
            point_diff[0] -= self.world_rect[0]
            point_diff[1] -= self.world_rect[1]
            distance = point_diff[0] ** 2 + point_diff[1] ** 2
            if distance < closest_d or closest_d == -1:
                closest = point
                closest_d = distance

        if closest_d == -1:
            return

        self.stick_to(closest)
