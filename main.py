import Engine.GameManager
import Engine.Input
from utils.rom.FilesystemViewer import FilesystemViewer
from utils.NodeEditor import NodeEditor
from utils.GDSEditor import GDSEditor
from utils.rom.rom_extract import clear_extracted
from utils.rom import RomSingleton
from event.EventPlayer import EventPlayer
from Engine.Debug import Debug
import pygame as pg
import LaytonLib.gds


class EventEditor:
    def __init__(self, event_id):
        self.event_id = event_id

        screen_size = (1920, 1080)

        self.gm = Engine.GameManager.GameManager(screen_size=screen_size, full_screen=False, log_fps=False,
                                                 name="Event Editor")
        self.inp = Engine.Input.Input()

        self.event_player = EventPlayer(self.event_id)
        self.node_editor = NodeEditor(pg.Rect(256 * 2, 0, screen_size[0] - 256 * 2, 1080 - 192 * 2))
        self.filesystem = FilesystemViewer(pg.Rect(0, 192*4, 256*3, screen_size[1] - 192 * 4))

    def load(self):
        self.event_player.reset()
        self.node_editor.load()
        self.filesystem.load()

        names = self.gds_to_images(self.event_player.event_data.event_gds)
        self.node_editor.generate_nodes(self.event_player.event_data.event_gds.commands, names)
        self.node_editor.select_node = self.node_selected

        self.event_player.run_gds_command()

        self.gm.tick()

    def gds_to_images(self, gds: LaytonLib.gds.GDSScript):
        transform_list = {
            0x2: "fade_in_both.png",
            0x3: "fade_out_both.png",
            0x4: "dialogue.png",
            0x21: "load_bg_btm.png",
            0x22: "load_bg_top.png",
            0x2a: "chr_show.png",
            0x2b: "chr_hide.png",
            0x2c: "chr_visible.png",
            0x30: "chr_slot.png",
            0x32: "fade_btm_in.png",
            0x33: "fade_btm_out.png",
            0x31: "wait.png",
            0x37: "bg_alpha.png",
            0x3f: "chr_anim.png",
            0x5d: "sad_sfx.png",
            0x6a: "bg_shake.png",
            0x87: "fade_out_top_timed.png",
            0x88: "fade_in_top_timed.png",
        }
        result = []
        commands_to_del = []
        for command in gds.commands:  # type: LaytonLib.gds.GDSCommand
            if command.command not in transform_list.keys():
                commands_to_del.append(command)
                Debug.log_warning(f"Removed command {hex(command.command)}. This event shouldn't be saved.", self)
                continue
            result.append(transform_list[command.command])
        for command in commands_to_del:
            gds.commands.remove(command)
        return result

    def reset_event_player(self):
        self.event_player.reset()
        self.event_player.run_gds_command()

    def run(self):
        while self.filesystem.running:
            self.gm.tick()
            if self.inp.get_key_down(pg.K_r):
                self.reset_event_player()
                continue
            if self.inp.get_key_down(pg.K_c):
                self.event_player.run_gds_command()
                continue
            dirties = []
            dirties.extend(self.event_player.run())
            dirties.extend(self.node_editor.run())
            dirties.extend(self.filesystem.run())
            pg.display.update(dirties)

        self.event_player.exit()
        self.node_editor.exit()
        self.filesystem.exit()

    def node_selected(self, node_id, node_info):
        self.event_player.reset(skip_fade_in=True)
        self.event_player.run_gds_command(run_until_command=node_id)


def test_event(event_id):
    event_editor = EventEditor(event_id)
    event_editor.load()
    event_editor.run()


if __name__ == '__main__':
    RomSingleton.RomSingleton("test_rom.nds")
    test_event(14230)
    clear_extracted()
    # test_event(14230)
