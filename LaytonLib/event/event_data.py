# Ported from shortbrim
import LaytonLib.binary as bin
import ndspy.rom
import LaytonLib.gds
import LaytonLib.filesystem as fs


class EventData:
    def __init__(self, rom: ndspy.rom.NintendoDSRom = None):
        self.rom = rom
        self.event_id = 0

        self.event_gds: LaytonLib.gds.GDSScript = None
        self.event_texts: fs.PlzFile = None

        self.map_top_id = 0
        self.map_bottom_id = 0
        self.characters = []
        self.characters_pos = []
        self.characters_shown = []
        self.characters_anim_index = []

    def set_event_id(self, new_id):
        self.event_id = new_id

    def resolve_event_id(self):
        prefix = self.event_id // 1000
        postfix = self.event_id % 1000
        complete = str(prefix)
        if prefix == 24:
            if postfix < 300:
                complete += "a"
            elif postfix < 600:
                complete += "b"
            else:
                complete += "c"
        return str(prefix), str(postfix).zfill(3), complete

    def load_from_rom(self):
        if self.rom is None:
            return
        prefix, postfix, complete = self.resolve_event_id()
        packed_id = self.rom.filenames.idOf(f"data_lt2/event/ev_d{complete}.plz")
        events_packed = fs.PlzFile(self.rom, packed_id)
        file_id = events_packed.idOf(f"d{complete}_{postfix}.dat")
        self.load(events_packed.files[file_id])
        self.load_gds()
        self.load_texts()

    def load(self, data: bytes):
        print(data)
        reader = bin.BinaryReader(data=data)
        self.map_bottom_id = reader.readU16()
        self.map_top_id = reader.readU16()

        reader.c += 2

        for _indexChar in range(8):
            temp_char = reader.readU8()
            if temp_char != 0:
                self.characters.append(temp_char)
        for _indexChar in range(8):
            self.characters_pos.append(reader.readU8())
        for _indexChar in range(8):
            if reader.readU8() == 0:
                self.characters_shown.append(False)
            else:
                self.characters_shown.append(True)
        for _indexChar in range(8):
            self.characters_anim_index.append(reader.readU8())

    def load_gds(self):
        prefix, postfix, complete = self.resolve_event_id()
        packed_id = self.rom.filenames.idOf(f"data_lt2/event/ev_d{complete}.plz")
        events_packed = fs.PlzFile(self.rom, packed_id)
        file_id = events_packed.idOf(f"e{complete}_{postfix}.gds")
        self.event_gds = LaytonLib.gds.GDSScript.from_bytes(events_packed.files[file_id])

    def load_texts(self):
        prefix, postfix, complete = self.resolve_event_id()
        event_texts_id = self.rom.filenames.idOf(f"data_lt2/event/en/ev_t{complete}.plz")
        self.event_texts = fs.PlzFile(self.rom, event_texts_id)

    def get_text(self, text_num):
        prefix, postfix, complete = self.resolve_event_id()
        text_id = self.event_texts.idOf(f"t{prefix}_{postfix}_{text_num}.gds")
        return LaytonLib.gds.GDSScript.from_bytes(self.event_texts.files[text_id])


if __name__ == '__main__':
    rom = ndspy.rom.NintendoDSRom.fromFile("../../test_rom.nds")
    event_dat = EventData(rom)
    event_dat.set_event_id(10080)
    event_dat.load_from_rom()
    print(event_dat.characters)
