import gl_var
from CustomScenes.gameplay import GamePlaySC
from CustomScenes.menus import MainMenuSC, RunOverSC
from Illusion.game_manager import IllusionBuiltInsPreset


class Game(IllusionBuiltInsPreset):
    def __init__(self,hws):
        super().__init__(hws)

        self._global_objects.add_font("title_font","Chonk.otf")
        self._global_objects.add_font("text_font","Genrik7.otf")

        self._global_objects.add_custom_object("btn_sprites",self._importer.return_import_animated_sprite("button.png",3,gl_var.btn_size))
        self._importer.import_img("gameplay_bg","bg/gameplay.png",2)
        self._importer.import_animated_sprite("boss_animation_vfx","vfx/boss_animation.png",3,3)
        self._importer.import_animated_sprite("health_indicator_hud","hud/health_indicator.png",2,4)

        self._scene_manager.add_scene(MainMenuSC(self._importer, self._assets, self._music_manager, self._global_objects))
        self._scene_manager.add_scene(GamePlaySC(self._importer, self._assets, self._music_manager, self._global_objects))
        self._scene_manager.add_scene(RunOverSC(self._importer, self._assets, self._music_manager, self._global_objects))

    def get_cur_scene(self):
        return self._scene_manager.get_cur_scene()