import Engine.Animation
import Engine.Sprite


class EventCharacter(Engine.Animation.Animation):
    FACING_LEFT = 1
    FACING_RIGHT = 2

    SLOT_MAX = 6
    SLOT_OFFSET = {0: 0, 1: 0,
                   2: 0, 3: 0,
                   4: 52, 5: 52,
                   6: 0}
    SLOT_ON_LEFT = [0, 3, 4]  # Verified against game binary
    SLOT_ON_RIGHT = [2, 5, 6]

    def __init__(self, groups):
        super(EventCharacter, self).__init__(groups)
        self.orientation = EventCharacter.FACING_RIGHT
        self.draw_alignment[1] = Engine.Sprite.Sprite.ALIGNMENT_BOTTOM
        self.world_rect.y += 192 // 2
        self.slot = 0
        self.character_mouth = Engine.Animation.Animation([])
        self.character_mouth.layer = -10
        self.character_mouth.add(groups)

        self.groups_perseverance = groups

        self.char_id = 0

    def check_orientation(self):
        if self.slot in EventCharacter.SLOT_ON_LEFT:
            self.orientation = EventCharacter.FACING_RIGHT
        else:
            self.orientation = EventCharacter.FACING_LEFT

    def update_(self):
        super(EventCharacter, self).update_()
        self.check_orientation()
        if self.orientation == EventCharacter.FACING_RIGHT:
            self.flip(True, False)
        else:
            self.flip(False, False)

        mouth_offset = [self.current_tag["child_x"], self.current_tag["child_y"]]

        if self.orientation == EventCharacter.FACING_RIGHT:
            offset = EventCharacter.SLOT_OFFSET[self.slot] - 256 // 2
            self.draw_alignment[0] = self.ALIGNMENT_RIGHT
        else:
            offset = (256 // 2) - EventCharacter.SLOT_OFFSET[self.slot]
            self.draw_alignment[0] = self.ALIGNMENT_LEFT
        self.world_rect.x = offset

        if self.character_mouth is not None:
            if self.orientation == EventCharacter.FACING_RIGHT:
                mouth_offset[0] = self.world_rect.w - mouth_offset[0]
                self.character_mouth.draw_alignment[0] = self.ALIGNMENT_LEFT
                self.character_mouth.flip(True, False)
            else:
                mouth_offset[0] = mouth_offset[0] - self.world_rect.w
                self.character_mouth.draw_alignment[0] = self.ALIGNMENT_RIGHT
                self.character_mouth.flip(False, False)

            self.character_mouth.world_rect.x = self.world_rect.x + mouth_offset[0]
            self.character_mouth.world_rect.y = self.world_rect.y - self.world_rect.h + mouth_offset[1]
            self.character_mouth.draw_alignment[1] = self.ALIGNMENT_TOP
            self.character_mouth.set_tag_by_num(self.current_tag["child_index"])
            if self.current_tag["child_index"] == 0:
                self.character_mouth.kill()
            elif self.alive() and not self.character_mouth.alive():
                self.character_mouth.add(self.groups())
            self.character_mouth.dirty = 1
        self.dirty = 1

    def show(self):
        if not self.alive():
            self.add(self.groups_perseverance)
            if self.character_mouth is not None:
                self.character_mouth.add(self.groups_perseverance)
        self.dirty = 1
        if self.character_mouth is not None:
            self.character_mouth.dirty = 1

    def hide(self):
        if self.alive():
            self.kill()
            if self.character_mouth is not None:
                self.character_mouth.kill()
        self.dirty = 1
        if self.character_mouth is not None:
            self.character_mouth.dirty = 1