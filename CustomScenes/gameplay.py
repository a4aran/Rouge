import pygame
from pygame import SRCALPHA

import c_objects.world
import gl_var
from Illusion.frame_data_f import FrameData
from Illusion.go import GlobalObjects
from Illusion.importer import Importer, Assets, MusicManager
from Illusion.scene import Scene
from c_objects.world import World


class GamePlaySC(Scene):
    def __init__(self, importer: Importer, assets: Assets, music_manager: MusicManager, global_objects: GlobalObjects):
        super().__init__(importer, assets, music_manager, global_objects)

        self.set_ui_to_background("default")
        temp = self.get_ui("default")
        temp.new_img("overlay",importer.get_sprite("gameplay_bg"),gl_var.window_center)

        self.paused = False
        self._objs.append(c_objects.world.World())

        self.create_ui("hud")
        temp = self.get_ui("hud")
        temp_surf = pygame.Surface((120,120))
        temp_surf.fill((0,0,0))
        sq_pos = (75,500)
        hp_pos = (75,100)
        temp.new_img("hp_bg",importer.get_animated_sprite("health_indicator_hud")[0],hp_pos)
        temp.new_img("hp_indicator",importer.get_animated_sprite("health_indicator_hud")[1],hp_pos)
        temp.new_text_display("hp_amount",global_objects.get_font("text_font"),hp_pos)
        temp.get_text_display("hp_amount").set_all((255,255,255),45,"")


        temp.new_img("square_bg",temp_surf,sq_pos)
        temp.new_img("super_square",pygame.Surface((100,100),SRCALPHA),sq_pos)

        self.create_ui("boss_animation")
        ba_ui = self.get_ui("boss_animation")
        temp_img = pygame.Surface((900,600),SRCALPHA)
        temp_img.fill((0,0,0,64))
        ba_ui.new_img("bg",temp_img,gl_var.window_center)
        ba_ui.new_animation("boss_shake",importer.get_animated_sprite("boss_animation_vfx"),gl_var.window_center,10)
        ba_ui.new_text_display("wave_info",global_objects.get_font("title_font"),gl_var.window_center)
        ba_ui.get_text_display("wave_info").set_all((0,0,0),80,"")
        ba_ui.should_show = False

        self.create_ui("pause")
        p_ui = self.get_ui("pause")
        temp_img.fill((0,0,0,128))
        p_ui.new_img("bg",temp_img,gl_var.window_center)
        p_ui.new_text_display("pause_text",global_objects.get_font("title_font"),gl_var.window_center)
        temp_txt = p_ui.get_text_display("pause_text")
        temp_txt.set_all((255,255,255),40,["Game Paused"])
        p_ui.should_show = self.paused

        self.vfx_to_show = [False,None]

        self.vfx_dict = {
            "wave_start": "boss_animation"
        }

        self.vfx_reset_f = False

        self.key_press_once = [0,0.2,False]\

        self.data["wave"] = 0

        self.super_square = pygame.Surface((100,100),SRCALPHA)
        self.super_percent = 1

        temp_img_import = importer.get_animated_sprite("health_indicator_hud")[1]
        self.hp_indicator = pygame.Surface(temp_img_import.get_size(),SRCALPHA)
        self.hp_indicator.blit(temp_img_import,(0,0))
        self.hp_percent = 1

        self.last_frame_hp = 0

    def _update(self, frame_data: FrameData):
        temp_vfx = self.vfx_to_show[0]
        super()._update(frame_data)
        temp = self._objs[0]
        if isinstance(temp,World):
            if temp.player.health <= 0:
                self.edit_change_scene_data(True,3)
            if temp.should_show_vfx:
                self.vfx_to_show[0] = True
                self.vfx_to_show[1] = temp.vfx_to_show
            else:
                self.vfx_to_show = [False, None]
            self.data["wave"] = temp.wave_count
        if temp.player.super["cooldown"][2]:
            self.super_percent = 1
        else:
            self.super_percent = temp.player.super["cooldown"][0] / temp.player.super["cooldown"][1]

        if self.super_percent == 1:
            self.super_square.fill((255,0,0))
        else:
            self.super_square.fill((255,255,255,255 * self.super_percent))

        self.hp_percent = temp.player.health / temp.player.max_health

        if frame_data.keys[pygame.K_ESCAPE] and not self.key_press_once[2] and not self.vfx_to_show[0]:
            self.paused = not self.paused
            temp.game_paused = self.paused
            self.key_press_once[2] = True

        if self.key_press_once[2]:
            self.key_press_once[0] += frame_data.dt
            if self.key_press_once[0] >= self.key_press_once[1]:
                self.key_press_once[0] = 0
                self.key_press_once[2] = False

        self.get_ui("pause").should_show = self.paused

        if self.vfx_to_show[0]:
            name = self.vfx_to_show[1]
            if name in self.vfx_dict:
                self.get_ui(self.vfx_dict[name]).should_show = True
        if temp_vfx != self.vfx_to_show[0]:
            for name in self.vfx_dict:
                self.get_ui(self.vfx_dict[name]).should_show = False

        temp_ui = self.get_ui("boss_animation")
        if temp_ui.should_show:
            temp_txt = temp_ui.get_text_display("wave_info")
            if not temp_txt.get_text() == [f'Wave {temp.wave_count}']:
                temp_txt.set_text([f'Wave {temp.wave_count}'])

        temp_b_img = self.hp_indicator.copy()
        temp_b_img.set_alpha(255 * self.hp_percent)
        self.get_ui("hud").get_img("super_square").change_img(self.super_square)
        self.get_ui("hud").get_img("hp_indicator").change_img(temp_b_img)

        if temp.player.health != self.last_frame_hp:
            self.last_frame_hp = temp.player.health
            self.get_ui("hud").get_text_display("hp_amount").set_text([f'{self.last_frame_hp}'])

    def on_changed_to(self,previous_scene_id):
        self._objs[0].reset()