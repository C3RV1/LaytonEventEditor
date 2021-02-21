import ndspy.rom


class RomSingleton:
    __instance = None
    __inited = False

    @staticmethod
    def __new__(cls, *args, **kwargs):
        if not isinstance(RomSingleton.__instance, RomSingleton):
            RomSingleton.__instance = super(RomSingleton, cls).__new__(cls)
        return RomSingleton.__instance

    def __init__(self, rom_path=None):
        if not RomSingleton.__inited:
            if rom_path is None:
                raise Exception("Rom can't be none")
            self.rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
            RomSingleton.__inited = True
