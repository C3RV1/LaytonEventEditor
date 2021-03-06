import Engine.UI.UIElement
import Engine.UI.Text
import Engine.Sprite
import Engine.GameManager
import Engine.Input
from Engine.Debug import Debug
from event.EventCharacter import EventCharacter
from utils.rom.rom_extract import load_animation
from typing import Optional
import pygame as pg
import utils.SADLStreamPlayer
from utils.rom.rom_extract import load_effect


class EventDialogue(Engine.UI.UIElement.UIElement, Engine.Sprite.Sprite):
    NUMBER_OF_LINES = 5

    def __init__(self, groups, voice_player: utils.SADLStreamPlayer.SoundPlayer):
        Engine.UI.UIElement.UIElement.__init__(self)
        Engine.Sprite.Sprite.__init__(self, groups)
        self.gm = Engine.GameManager.GameManager()

        self.check_interacting = self._check_interacting
        self.pre_interact = self.pre_interact_

        self.interact = self._interact
        self.inner_text = []

        self.char_name = Engine.Sprite.Sprite([])
        self.char_name.layer = 101
        self.char_name.add(groups)
        self.char_name.draw_alignment = [self.ALIGNMENT_RIGHT, self.ALIGNMENT_TOP]

        self.inp = Engine.Input.Input()

        self.current_line = 0
        self.current_pause = 0
        self.text_left_to_do = ""
        self.current_text = ""
        self.paused = False

        self.current_time_between_progress = 0
        self.time_to_progress = .02

        self.character_talking: Optional[EventCharacter] = None

        self.voice_player = voice_player
        self.voice_line = -1

    def set_talking(self):
        # If there is a voice line play it (first we stop it)
        self.voice_player.stop()
        if self.voice_line != -1:
            sfx = load_effect(f"data_lt2/stream/event/?/{str(self.voice_line).zfill(3)}_{self.current_pause}.SAD")
            self.voice_player.start_sound(sfx)

        if self.character_talking is None:
            return

        # * + anim name is talking animation
        current_tag = self.character_talking.current_tag["name"]
        if not current_tag.startswith("*"):
            self.character_talking.set_tag("*" + current_tag)
            if self.character_talking.current_tag["name"] != "*" + current_tag:
                self.character_talking.set_tag("*" + current_tag + " ")
            # Update character_talking
            self.character_talking.update_()

    def set_not_talking(self):
        if self.character_talking is None:
            return
        current_tag = self.character_talking.current_tag["name"]
        if current_tag.endswith(" "):
            current_tag = current_tag[:-1]
        if current_tag.startswith("*"):
            self.character_talking.set_tag(current_tag[1:])
            self.character_talking.update_()

    def init_position(self):
        # Init dialogue positions
        for line in range(self.NUMBER_OF_LINES):
            new_text = Engine.UI.Text.Text([])
            new_text.layer = 120
            new_text.add(self.groups())
            size = 16
            new_text.set_font("data_permanent/fonts/font_event", [9, 12], is_font_map=True)
            new_text.world_rect.x = (- 256 // 2) + 10
            new_text.world_rect.y = self.world_rect.y - self.world_rect.h + 19 + line * size
            new_text.draw_alignment = [new_text.ALIGNMENT_RIGHT, new_text.ALIGNMENT_TOP]
            self.inner_text.append(new_text)
        self.char_name.world_rect.y = self.world_rect.y - self.world_rect.h
        self.char_name.world_rect.x = - 256 // 2

    # Check if we are interacting with the dialogue (UIElement)
    def _check_interacting(self):
        if self.finished and not self.paused:
            self.voice_player.stop()
            self.interacting = False
            return
        self.interacting = True

    # Once we start to interact we set talking (UIElement)
    def pre_interact_(self):
        self.set_talking()

    # When we are interacting (UIElement)
    def _interact(self):
        # Get if the mouse was pressed in the display port of the current camera (bottom camera)
        mouse_pressed = self.inp.get_mouse_down(1) and \
                        self.current_camera.display_port.collidepoint(self.inp.get_screen_mouse_pos())
        if self.paused:
            if mouse_pressed:
                self.unpause()
            return
        if mouse_pressed:
            self.complete()
            return

        # See if we have to progress the text
        self.current_time_between_progress += self.gm.delta_time
        while self.current_time_between_progress > self.time_to_progress:
            self.current_time_between_progress -= self.time_to_progress
            self.progress_text()

    def progress_text(self):
        # TODO: commands starting with & (event 10060)
        if self.text_left_to_do.startswith("@B"):  # Next line
            self.current_line += 1
            self.current_text = ""
            self.text_left_to_do = self.text_left_to_do[2:]
            return
        elif self.text_left_to_do.startswith("@p"):  # Pause
            self.current_pause += 1
            self.pause()
            self.text_left_to_do = self.text_left_to_do[2:]
            return
        elif self.text_left_to_do.startswith("@c"):  # Next "page
            self.reset_texts()
            self.text_left_to_do = self.text_left_to_do[2:]
            return

        # Move one character from self.text_left_to_do to current_text
        self.current_text += self.text_left_to_do[:1]
        self.text_left_to_do = self.text_left_to_do[1:]

        # Update current text object
        self.inner_text[self.current_line].set_text(self.current_text, color=pg.Color(0, 0, 0), bg_color=[0, 255, 0],
                                                    mask_color=[0, 255, 0])

        # If we have finished we pause
        if self.finished:
            self.pause()

    # Complete until we pause
    def complete(self):
        while not self.paused and not self.finished:
            self.progress_text()

    # Reset the texts
    def reset_texts(self):
        self.current_line = 0
        self.current_text = ""
        for inner_txt in self.inner_text:
            inner_txt.set_text("")

    # Reset all (texts, paused, and current_pause)
    def reset_all(self):
        self.current_pause = 0
        self.paused = False
        self.reset_texts()

    # Init character name sprite
    def init_char_name(self):
        load_animation(f"data_lt2/ani/eventchr/?/chr{self.character_talking.char_id}_n.arc", self.char_name)

    # Pause the text
    def pause(self):
        self.paused = True
        self.set_not_talking()

    # Unpause the text
    def unpause(self):
        self.paused = False
        if not self.finished:
            self.set_talking()

    # The game uses some substitutions to represent certain characters
    # For example: <''> corresponds to a "
    # This function 'fixes' this substitutions
    def replace_substitutions(self):
        subs_dict = {"<''>": "\"",
                     "<^?>": "¿",
                     "<'e>": "é",
                     "<'a>": "á",
                     "<'o>": "ó",
                     "<'i>": "í",
                     "<'u>": "ú",
                     "<^!>": "¡"}
        for key, sub in subs_dict.items():
            self.text_left_to_do = self.text_left_to_do.replace(key, sub)

    @property
    def finished(self):
        return self.text_left_to_do == ""
