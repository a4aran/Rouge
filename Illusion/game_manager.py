import pygame

import window_size
from Illusion import go
from Illusion.go import GlobalObjects
from Illusion.importer import MusicManager
from Illusion.scene import Scene
from Illusion.frame_data_f import FrameData
from Illusion.importer import Importer, Assets
from Illusion.scene_manager import SceneManager


class GameManagerPreset:
    def __init__(self,hardware_sound: bool):
        self._scene_manager = SceneManager()
        self._importer = Importer(hardware_sound)
        self._assets = Assets()
        self._music_manager = MusicManager(hardware_sound)
        self._global_objects = go.GlobalObjects()

        self._importer.set_img_prefix("./assets/textures/static/")
        self._importer.set_animated_sprite_prefix("./assets/textures/animated/")
        self._importer.set_sound_prefix("./assets/sounds/effects/")
        self._music_manager.set_path_prefix("./assets/sounds/music/")

    def update_and_draw(self,frame_data: FrameData,surface: pygame.Surface):
        self._scene_manager.update_and_draw(frame_data,surface)

class IllusionBuiltInsPreset(GameManagerPreset):
    def __init__(self,hardware_sound: bool):
        super().__init__(hardware_sound)

        self._importer.set_animated_sprite_prefix("./assets/built-in-assets/")
        self._importer.set_sound_prefix("./assets/built-in-assets/")

        self._importer.import_animated_sprite("b_logo","logo.png",13,(64,192))

        self._importer.import_sound("b_successful_select","select_successful.wav")
        self._importer.import_sound("b_denied","select_denied.wav")

        self._importer.import_sound("b_logo_sound","logo_sound.wav")

        self._scene_manager.add_scene(self.__LoadSc(self._importer,self._assets,self._music_manager,self._global_objects))

        self._importer.set_img_prefix("./assets/textures/static/")
        self._importer.set_animated_sprite_prefix("./assets/textures/animated/")
        self._importer.set_sound_prefix("./assets/sounds/effects/")
        self._music_manager.set_path_prefix("./assets/sounds/music/")


    class __LoadSc(Scene):
        def __init__(self, importer: Importer, assets: Assets,music_manager: MusicManager,gos: GlobalObjects):
            super().__init__(importer, assets,music_manager,gos)
            temp_ui = self.get_ui("default")
            temp_ui.new_animation("logo",importer.get_animated_sprite("b_logo"),(window_size.width / 2, window_size.height / 2),10,1)
            importer.play_sound("b_logo_sound")
            self.anim_cooldown = 0
            self.fill_color = (0,80,90)


        def _update(self, frame_data: FrameData):
            if self.get_ui("default").get_animation("logo").is_done():
                self.anim_cooldown += frame_data.dt
            if self.anim_cooldown >= 0.75:
                self.edit_change_scene_data(True,1)
            super()._update(frame_data)