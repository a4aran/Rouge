import gl_var
from CustomScenes.gameplay import GamePlaySC
from CustomScenes.menus import MainMenuSC, RunOverSC, CharacterSelectionSC
from Illusion.game_manager import IllusionBuiltInsPreset


class Game(IllusionBuiltInsPreset):
    def __init__(self,hws):
        super().__init__(hws)

        self._global_objects.add_font("title_font","Chonk.otf")
        self._global_objects.add_font("text_font","Genrik7.otf")

        self._global_objects.add_custom_object("btn_sprites",self._importer.return_import_animated_sprite("button.png",3,gl_var.btn_size))
        self._global_objects.add_custom_object("vertical_btn_sprites",self._importer.return_import_animated_sprite("vertical_button.png",3,gl_var.vertical_btn_size))
        self._importer.import_img("gameplay_bg","bg/gameplay.png",2)

        self._global_objects.add_custom_object("player0_icon",self._importer.return_import_img("placeholder.png",(320,320)))

        self._importer.import_animated_sprite("boss_animation_vfx","vfx/boss_animation.png",3,3)
        self._importer.import_animated_sprite("health_indicator_hud","hud/health_indicator.png",2,4)
        self._importer.import_animated_sprite("super_indicator_hud","hud/super_indicator.png",3,4)
        self._importer.import_animated_sprite("firerate_indicator_hud","hud/firerate_indicator.png",2,4)
        self._importer.import_img("damage_hud","hud/damage_drop.png",4)
        self._importer.import_img("pierce_hud","hud/pierce_arrow.png",4)
        self._importer.import_img("speed_hud","hud/speed_bullet.png",4)

        self._global_objects.add_custom_object("heart_up",self._importer.return_import_animated_sprite("upgrades/heal.png",2,4))
        self._global_objects.add_custom_object("level_1_up",self._importer.return_import_animated_sprite("upgrades/level_1.png",2,4))
        self._global_objects.add_custom_object("level_2_up",self._importer.return_import_animated_sprite("upgrades/level_2.png",2,4))
        self._global_objects.add_custom_object("level_3_up",self._importer.return_import_animated_sprite("upgrades/level_3.png",2,4))
        self._global_objects.add_custom_object("level_4_up",self._importer.return_import_animated_sprite("upgrades/level_4.png",2,4))

        self._global_objects.add_custom_object("ice_cube_enemy_sprite",self._importer.return_import_animated_sprite("entities/enemies/ice_slider.png",2,2))

        self._global_objects.add_custom_object("chaos_boss_sprites",self._importer.return_import_animated_sprite("entities/bosses/chaos.png",3,4))

        self._global_objects.add_custom_object("status_effect_freeze_16",self._importer.return_import_img("status_effects/freeze/16.png",4))

        self._scene_manager.add_scene(MainMenuSC(self._importer, self._assets, self._music_manager, self._global_objects))
        self._scene_manager.add_scene(CharacterSelectionSC(self._importer,self._assets,self._music_manager,self._global_objects))
        self._scene_manager.add_scene(GamePlaySC(self._importer, self._assets, self._music_manager, self._global_objects))
        self._scene_manager.add_scene(RunOverSC(self._importer, self._assets, self._music_manager, self._global_objects))

    def get_cur_scene(self):
        return self._scene_manager.get_cur_scene()