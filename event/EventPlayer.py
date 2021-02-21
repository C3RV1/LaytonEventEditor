from utils import TwoScreenRenderer
from utils.rom import RomSingleton
from utils import ScreenFader, ScreenShaker
import Engine.GameManager
import Engine.Sprite
import Engine.Input
import Engine.UI.UIManager
from Engine.Debug import Debug
import LaytonLib.event.event_data as evdat
import LaytonLib.gds
import pygame as pg
from event.EventCharacter import EventCharacter
from event.EventDialogue import EventDialogue
from utils.rom.rom_extract import load_animation, load_bg, clear_extracted, ORIGINAL_FPS, load_effect


class EventPlayer(TwoScreenRenderer.TwoScreenRenderer):
    def __init__(self, event_id):
        super(EventPlayer, self).__init__()
        self.event_id = event_id

        self.inp = Engine.Input.Input()

        self.event_data = evdat.EventData(rom=RomSingleton.RomSingleton().rom)
        self.event_data.set_event_id(self.event_id)
        self.event_data.load_from_rom()

        self.top_bg = ScreenShaker.ScreenShaker([])
        self.top_bg.layer = -1000
        self.top_bg.post_shake = lambda: self.run_gds_command()

        self.bottom_bg = ScreenShaker.ScreenShaker([])
        self.bottom_bg.layer = -1000
        self.bottom_bg.post_shake = lambda: self.run_gds_command()

        self.top_fader = ScreenFader.ScreenFader([])
        self.top_fader.on_finish_fade = lambda fade_type: self.run_gds_command()

        self.bottom_fader = ScreenFader.ScreenFader([])
        self.bottom_fader.on_finish_fade = lambda fade_type: self.run_gds_command()

        self.back_translucent = Engine.Sprite.Sprite([])
        self.back_translucent.layer = -100
        self.back_translucent.image = pg.Surface([256, 192])
        self.back_translucent.image.fill(pg.Color(0, 0, 0))
        self.back_translucent.reset_world_rect()

        self.characters = {}
        self.char_order = []

        self.dialogue: EventDialogue = None

    def reset(self):
        self.dialogue = EventDialogue([])
        self.dialogue.layer = 100
        self.dialogue.post_interact = self.post_dialogue

        self.current_gds_command = 0
        self.wait_timer = 0

        self.bottom_screen_group.remove(self.bottom_screen_group.sprites())
        self.top_screen_group.remove(self.top_screen_group.sprites())

        self.top_fader.set_fade(self.top_fader.FADING_OUT, False)
        self.top_fader.current_time = 0
        self.top_fader.update_fade()

        self.bottom_fader.set_fade(self.bottom_fader.FADING_OUT, False)
        self.bottom_fader.current_time = 0
        self.bottom_fader.update_fade()

        self.back_translucent.image.set_alpha(120)

        self.characters = {}
        self.char_order = []

        self.current_gds_command = 0
        self.wait_timer = 0

        self.top_screen_group.add([self.top_fader, self.top_bg])
        self.bottom_screen_group.add([self.dialogue, self.bottom_bg, self.bottom_fader, self.back_translucent])

        self.load()

    def hide_dialogue(self):
        for text in self.dialogue.inner_text:
            text.kill()
        self.dialogue.char_name.kill()
        self.dialogue.kill()
        self.bottom_screen_camera.draw(self.bottom_screen_group, dirty_all=True)

    def show_dialogue(self):
        for text in self.dialogue.inner_text:
            text.add(self.bottom_screen_group)
        self.dialogue.char_name.add(self.bottom_screen_group)
        self.dialogue.add(self.bottom_screen_group)
        print(self.dialogue.groups())
        self.bottom_screen_camera.draw(self.bottom_screen_group, dirty_all=True)

    def start_dialogue(self, command: LaytonLib.gds.GDSCommand):
        dialogue_id = command.params[0]
        dialogue_gds = self.event_data.get_text(dialogue_id)
        self.show_dialogue()
        self.dialogue.reset()
        self.dialogue.text_left_to_do = dialogue_gds.params[4]
        Debug.log(f"Dialogue: {self.dialogue.text_left_to_do}", self)
        self.dialogue.replace_substitutions()

        if dialogue_gds.params[0] != 0:
            self.dialogue.character_talking = self.characters[dialogue_gds.params[0]]
            self.dialogue.init_char_name()

            if dialogue_gds.params[1] != "NONE":
                self.dialogue.character_talking.set_tag(dialogue_gds.params[1])

            self.dialogue.character_talking.update_()
        else:
            self.dialogue.character_talking = None
            self.dialogue.char_name.kill()

    def post_dialogue(self):
        self.hide_dialogue()
        self.run_gds_command()

    def load(self):
        load_animation(f"data_lt2/ani/event/twindow.arc", self.dialogue)
        self.dialogue.draw_alignment[1] = self.dialogue.ALIGNMENT_BOTTOM
        self.dialogue.world_rect.y += 192 // 2
        self.dialogue.init_position()
        self.hide_dialogue()

        self.top_fader.fade_in(False)
        self.bottom_fader.fade_in(False)

        load_bg(f"data_lt2/bg/event/sub{self.event_data.map_top_id}.arc", self.top_bg)
        load_bg(f"data_lt2/bg/map/main{self.event_data.map_bottom_id}.arc", self.bottom_bg)

        for char_num, character in enumerate(self.event_data.characters):
            new_character = EventCharacter(self.bottom_screen_group)
            new_character.char_id = character

            load_animation(f"data_lt2/ani/eventchr/chr{character}.arc", new_character)
            try:
                load_animation(f"data_lt2/ani/sub/chr{character}_face.arc", new_character.character_mouth)
            except:
                new_character.character_mouth.kill()
                new_character.character_mouth = None

            if self.event_data.characters_shown[char_num] == 0:
                new_character.hide()
            new_character.slot = self.event_data.characters_pos[char_num]
            new_character.set_tag_by_num(self.event_data.characters_anim_index[char_num])
            new_character.update_anim_frame()

            new_character.set_tag_by_num(self.event_data.characters_anim_index[char_num])
            new_character.update_anim_frame()

            new_character.update_()
            self.characters[character] = new_character
            self.char_order.append(character)

    def update(self):
        super().update()
        if self.inp.quit:
            self.running = False

        for character in self.characters.keys():
            character: EventCharacter = self.characters[character]
            character.update_animation(self.gm.delta_time)
            if character.character_mouth is not None:
                character.character_mouth.update_animation(self.gm.delta_time)

        self.top_fader.update_()
        self.bottom_fader.update_()
        self.bottom_bg.update_()

        if self.wait_timer > 0:
            self.wait_timer -= self.gm.delta_time
            if self.wait_timer <= 0:
                self.run_gds_command()

        Engine.UI.UIManager.UIManager.update([self.dialogue])

    def run_gds_command(self):
        while True:
            if self.current_gds_command >= len(self.event_data.event_gds.commands):
                break
            next_command: LaytonLib.gds.GDSCommand = self.event_data.event_gds.commands[self.current_gds_command]
            self.current_gds_command += 1
            if next_command.command == 0x2:
                Debug.log("Fading in both screens", self)
                self.top_fader.fade_in(True)
                self.bottom_fader.fade_in(False)
                return
            elif next_command.command == 0x3:
                Debug.log("Fading out both screens", self)
                self.top_fader.fade_out(True)
                self.bottom_fader.fade_out(False)
                return
            elif next_command.command == 0x4:
                Debug.log(f"Starting dialogue {next_command.params[0]}", self)
                self.start_dialogue(next_command)
                return
            elif next_command.command == 0x21:
                path = ".".join(next_command.params[0].split(".")[:-1]) + ".arc"  # Change extension
                Debug.log(f"Loading BG on bottom {path}", self)
                load_bg("data_lt2/bg/" + path, self.bottom_bg)
                self.back_translucent.image.set_alpha(0)
                self.back_translucent.dirty = 1
            elif next_command.command == 0x22:
                path = ".".join(next_command.params[0].split(".")[:-1]) + ".arc"  # Change extension
                Debug.log(f"Loading BG on top {path}", self)
                load_bg("data_lt2/bg/" + path, self.top_bg)
            elif next_command.command == 0x2a:
                Debug.log(f"Showing character {next_command.params[0]}", self)
                char_id = self.char_order[next_command.params[0]]
                self.characters[char_id].show()
            elif next_command.command == 0x2b:
                Debug.log(f"Hiding character {next_command.params[0]}", self)
                char_id = self.char_order[next_command.params[0]]
                self.characters[char_id].hide()
            elif next_command.command == 0x2C:
                Debug.log(f"Setting character {next_command.params[0]} visibility "
                          f"to {next_command.params[1] > 0}", self)
                char_id = self.char_order[next_command.params[0]]
                if next_command.params[1] > 0:
                    self.characters[char_id].show()
                else:
                    self.characters[char_id].hide()
            elif next_command.command == 0x30:
                Debug.log(f"Setting character {next_command.params[0]} slot to {next_command.params[1]}", self)
                char_id = self.char_order[next_command.params[0]]
                char: EventCharacter = self.characters[char_id]
                char.slot = next_command.params[1]
                char.update_()
            elif next_command.command == 0x32:
                Debug.log(f"Fading bottom in", self)
                self.bottom_fader.fade_in(True)
                return
            elif next_command.command == 0x33:
                Debug.log("Fading bottom out", self)
                self.bottom_fader.fade_out(True)
                return
            elif next_command.command == 0x31:
                self.wait(next_command.params[0])
                Debug.log(f"Waiting {self.wait_timer}", self)
                return
            elif next_command.command == 0x37:
                Debug.log(f"Setting BG opacity to {next_command.params[3]}", self)
                self.back_translucent.image.set_alpha(next_command.params[3])
                self.back_translucent.dirty = 1
            elif next_command.command == 0x3f:
                Debug.log(f"Setting character {next_command.params[0]} animation to {next_command.params[1]}", self)
                self.characters[next_command.params[0]].set_tag(next_command.params[1])
            elif next_command.command == 0x5d:
                Debug.log(f"Playing SAD SFX {next_command.params[0]}", self)
                sfx_path = f"data_lt2/stream/ST_{str(next_command.params[0]).zfill(3)}.SAD"
                sfx = load_effect(sfx_path)
                sfx.play()
            elif next_command.command == 0x5e:
                Debug.log(f"SFX Sequenced {next_command.params}", self)
            elif next_command.command == 0x6a:
                Debug.log(f"Shaking screen bottom", self)
                self.bottom_bg.shake()
            elif next_command.command == 0x87:
                Debug.log(f"Fading out top in {next_command.params[0]} frames", self)
                self.top_fader.fade_out(True)
                self.top_fader.current_time = next_command.params[0] / ORIGINAL_FPS
                return
            elif next_command.command == 0x88:
                Debug.log(f"Fading in top in {next_command.params[0]} frames", self)
                self.top_fader.fade_in(True)
                self.top_fader.current_time = next_command.params[0] / ORIGINAL_FPS
                return
            else:
                Debug.log(f"Unknown dialogue {next_command}", self)
        Debug.log("Event execution finished", self)

    def wait(self, time):
        self.wait_timer = (time / ORIGINAL_FPS)

    def exit(self):
        clear_extracted()
        super().exit()
