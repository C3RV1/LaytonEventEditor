import Engine.Sprite
import os
import shutil
import LaytonLib.images.ani as ani
import LaytonLib.images.bg as bg
import PIL.Image as imgl
import json
import pygame as pg
from utils.rom import RomSingleton
import SADLpy.SADL

EXPORT_PATH = "data_extracted"
ORIGINAL_FPS = 60


def load_animation(path: str, sprite: Engine.Sprite.Sprite):
    rom = RomSingleton.RomSingleton().rom
    path = path.replace("?", "en")
    export_path = EXPORT_PATH + "/" + path
    if not os.path.isfile(export_path + ".png"):
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        anim = ani.AniFile(rom, rom.filenames.idOf(path))

        # Sprite Sheet
        pil_images = []
        for i in range(len(anim.images)):
            pil_images.append(anim.frame_to_PIL(i))
        width = sum([img.size[0] for img in pil_images])
        height = max([img.size[1] for img in pil_images])
        pil_sprite_sheet = imgl.new('RGB', (width, height))
        x_pos = 0
        for image in range(len(pil_images)):
            pil_sprite_sheet.paste(pil_images[image], [x_pos, 0])
            x_pos += pil_images[image].size[0]
        pil_sprite_sheet.save(export_path + ".png")

        sprite_info = {"frames": [], "meta": {"frameTags": []}}
        x_pos = 0
        for i in range(len(anim.images)):
            new_frame_info = {
                "frame": {"x": x_pos,
                          "y": 0,
                          "w": pil_images[i].size[0],
                          "h": pil_images[i].size[1]},
                "duration": None
            }
            sprite_info["frames"].append(new_frame_info)
            x_pos += pil_images[0].size[0]

        for i in range(len(anim.animations)):
            anim_anim: ani.Animation = anim.animations[i]
            new_tag_info = {
                "name": anim_anim.name,
                "frames": anim_anim.imageIndexes,
                "child_x": anim_anim.child_spr_x,
                "child_y": anim_anim.child_spr_y,
                "child_index": anim_anim.child_spr_index
            }
            for frame_num in range(len(anim_anim.imageIndexes)):
                frame = anim_anim.imageIndexes[frame_num]
                duration = int(anim_anim.frameDurations[frame_num] * 1000) // ORIGINAL_FPS  # Frames to ms
                sprite_info["frames"][frame]["duration"] = duration
            sprite_info["meta"]["frameTags"].append(new_tag_info)

        with open(export_path + ".json", "w") as anim_file:
            anim_file.write(json.dumps(sprite_info, indent=4))
    sprite.load_sprite_sheet(export_path)
    sprite.set_color_key(pg.color.Color(0, 248, 0))
    sprite.dirty = 1


def load_bg(path: str, sprite: Engine.Sprite.Sprite):
    rom = RomSingleton.RomSingleton().rom
    path = path.replace("?", "en")
    export_path = EXPORT_PATH + "/" + path + ".png"
    if not os.path.isfile(export_path):
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        bg_img = bg.BgFile(rom, rom.filenames.idOf(path))
        bg_img.img.save(export_path)
    sprite.load(export_path)
    sprite.dirty = 1


def load_effect(path: str) -> SADLpy.SADL.SADL:
    rom = RomSingleton.RomSingleton().rom
    path = path.replace("?", "en")
    sad_export_path = EXPORT_PATH + "/" + path
    if not os.path.isfile(sad_export_path):
        os.makedirs(os.path.dirname(sad_export_path), exist_ok=True)
        print(path)
        sound_data = rom.files[rom.filenames.idOf(path)]
        with open(sad_export_path, "wb") as sad_export_file:
            sad_export_file.write(sound_data)
    sadl = SADLpy.SADL.SADL(sad_export_path, 0, True)
    sadl.read_file()
    return sadl


def clear_extracted():
    shutil.rmtree(EXPORT_PATH)
