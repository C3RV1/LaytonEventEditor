import Engine.GameManager
import Engine.UI.Button
import Engine.UI.Text
import Engine.UI.UIElement
import Engine.UI.UIManager
import Engine.Camera
import Engine.Screen
import Engine.Input
import Engine.Sprite
from Engine import Renderer
import pygame as pg
from utils.rom.rom_extract import load_bg, load_animation
from utils.rom import RomSingleton


class ButtonWithText(Engine.UI.UIElement.UIElement, Engine.UI.Text.Text):
    def __init__(self, groups):
        Engine.UI.UIElement.UIElement.__init__(self)
        Engine.UI.Text.Text.__init__(self, groups)

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


class FilesystemViewer(Renderer.Renderer):
    def __init__(self, render_rect):
        super(FilesystemViewer, self).__init__()
        self.rom = RomSingleton.RomSingleton().rom

        self.group = pg.sprite.LayeredDirty()
        self.camera = Engine.Camera.Camera()
        self.camera.display_port = render_rect
        self.group.set_clip(self.camera.display_port)

        self.camera.cam_alignment = [Engine.Sprite.Sprite.ALIGNMENT_RIGHT, Engine.Sprite.Sprite.ALIGNMENT_BOTTOM]
        self.blank_surface.fill(pg.Color(20, 20, 20))

        self.preview_sprite = Engine.Sprite.Sprite([])
        self.preview_sprite.is_world = False
        self.preview_sprite.world_rect.x = 256 * 2
        self.preview_sprite.world_rect.y += 192

        self.current_content_buttons = []
        self.button_y = 0

    def fill(self):
        self.screen.fill(pg.Color(120, 120, 120), rect=self.camera.display_port)

    def load(self):
        # load_bg("data_lt2/bg/map/main10.arc", self.sprite_test)
        self.open_folder("data_lt2/")

    def change_to_folder(self, folder_path):
        print(f"Changing to folder: {folder_path}")
        self.open_folder(folder_path + "/")

    def change_to_file(self, file_path):
        print(f"Changing to file: {file_path}")
        if file_path.endswith(".arc"):
            try:
                load_bg(file_path, self.preview_sprite)
            except:
                load_animation(file_path, self.preview_sprite)
            self.preview_sprite.add(self.group)

    def create_new_folder(self, name, mapping_path):
        new_button = ButtonWithText(self.group)
        new_button.draw_alignment[0] = new_button.ALIGNMENT_RIGHT
        new_button.draw_alignment[1] = new_button.ALIGNMENT_TOP
        new_button.set_font(None, 22)
        new_button.set_text(name, color=(255, 0, 255))
        new_button.world_rect.y += self.button_y
        self.button_y += 22

        path = mapping_path
        new_button.command = lambda folder_path=path: self.change_to_folder(mapping_path)

        self.current_content_buttons.append(new_button)

    def create_new_file(self, name, mapping_path):
        new_button = ButtonWithText(self.group)
        new_button.draw_alignment[0] = new_button.ALIGNMENT_RIGHT
        new_button.draw_alignment[1] = new_button.ALIGNMENT_TOP
        new_button.set_font(None, 22)
        new_button.set_text(name, color=(255, 255, 0))
        new_button.world_rect.y += self.button_y
        self.button_y += 22

        path = mapping_path
        new_button.command = lambda folder_path=path: self.change_to_file(mapping_path)

        self.current_content_buttons.append(new_button)

    def open_folder(self, path, show_folders=True):
        self.button_y = 0
        for current_button in self.current_content_buttons:  # type: Engine.Sprite.Sprite
            current_button.kill()
        self.current_content_buttons = []
        if path == "/":
            folders = [fol[0] for fol in self.rom.filenames.folders]
            files = self.rom.filenames.files
        else:
            folders = [fol[0] for fol in self.rom.filenames[path].folders]
            files = self.rom.filenames[path].files
        if show_folders:
            if path != "/":
                self.create_new_folder("..", "/".join(path.split("/")[:-2]))
            for folder_name in folders:
                folder_path = path + folder_name
                self.create_new_folder(folder_name, folder_path)
        for file_name in files:
            file_path = path + file_name
            self.create_new_file(file_name, file_path)

    def clear(self):
        self.group.clear(self.screen, self.blank_surface)

    def update(self):
        if self.inp.quit:
            self.running = False
        if self.inp.get_mouse_up(4):
            self.camera.position[1] += 2000 * self.gm.delta_time
        if self.inp.get_mouse_up(5):
            self.camera.position[1] -= 2000 * self.gm.delta_time
        Engine.UI.UIManager.UIManager.update(self.current_content_buttons)

    def draw(self):
        self.camera.draw(self.group)
        dirty = self.group.draw(self.screen)
        return dirty
