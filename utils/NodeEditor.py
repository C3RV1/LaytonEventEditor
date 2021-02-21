from Engine import Renderer
import Engine.Camera
import pygame as pg
import Engine.UI.DraggableButton
import Engine.UI.UIManager
import Engine.UI.UIElement
import Engine.UI.DraggableCamera
import Engine.Input
import Engine.Sprite


class NodeEditor(Renderer.Renderer):
    def __init__(self):
        super(NodeEditor, self).__init__()

        self.group = pg.sprite.LayeredDirty()
        self.cam = Engine.UI.DraggableCamera.DraggableCamera()
        self.cam.display_port = pg.Rect(256, 0, 1280 - 256, 192*2)
        self.group.set_clip(self.cam.display_port)

        self.nodes = []
        self.nodes_data = []

        self.repaint_rect = []
        self.select_node = lambda node_info: None

    def generate_nodes(self, nodes, node_images):
        x = 0
        x_s = []
        y = 0
        self.nodes_data = nodes
        for i in range(len(nodes)):
            new_node = Engine.UI.DraggableButton.DraggableButton(self.group)
            new_node.press_command = lambda nid=i: self.select_node_(nid)
            new_node.load("data_permanent/sprites/" + node_images[i])
            new_node.world_rect.x = x
            new_node.world_rect.y = y
            x += new_node.world_rect.w + 10
            if i % 5 == 4:
                x_s.append(x)
                x = 0
                y += 50
            new_node.set_frame(0)
            self.nodes.append(new_node)
        self.cam.position[0] -= max(x_s) / 2 - 40
        self.cam.position[1] -= y / 2

    def select_node_(self, node_id):
        self.select_node(self.nodes_data[node_id])

    def clear(self):
        self.group.clear(self.screen, self.blank_surface)
        for repaint in self.repaint_rect:
            self.group.repaint_rect(repaint)
        self.repaint_rect = []

    def fill(self):
        self.screen.fill(pg.Color(50, 50, 50), rect=self.cam.display_port)

    def draw(self):
        self.cam.draw(self.group)
        dirty = self.group.draw(self.screen)
        return dirty

    def update(self):
        if self.inp.quit:
            self.running = False
        ui_elements = []
        ui_elements.extend(self.nodes)
        ui_elements.append(self.cam)
        Engine.UI.UIManager.UIManager.update(ui_elements)

    def post_draw(self):
        for node in range(len(self.nodes) - 1):
            node_obj: Engine.UI.DraggableButton.DraggableButton = self.nodes[node]
            node_obj2: Engine.UI.DraggableButton.DraggableButton = self.nodes[node + 1]
            x1 = node_obj.world_rect.x + (node_obj.world_rect.w // 2)
            y1 = node_obj.world_rect.y
            x2 = node_obj2.world_rect.x - (node_obj2.world_rect.w // 2)
            y2 = node_obj2.world_rect.y
            self.repaint_rect.append(self.cam.draw_line(x1, y1, x2, y2))
        return self.repaint_rect
