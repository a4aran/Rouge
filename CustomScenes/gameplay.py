from enum import Enum

import pygame
from pygame import SRCALPHA

import c_objects.world
import gl_var
import window_size
from Illusion.frame_data_f import FrameData
from Illusion.go import GlobalObjects
from Illusion.importer import Importer, Assets, MusicManager
from Illusion.scene import Scene
from c_objects.upgrader import Upgrader
from c_objects.world import World


class GamePlaySC(Scene):
    class State(Enum):
        PLAYING = 0
        UPGRADE = 1

    def __init__(self, importer: Importer, assets: Assets, music_manager: MusicManager, global_objects: GlobalObjects):
        super().__init__(importer, assets, music_manager, global_objects)

        self.set_ui_to_background("default")
        temp = self.get_ui("default")
        temp.new_img("overlay",importer.get_sprite("gameplay_bg"),gl_var.window_center)

        self.paused = False
        self._objs.append(c_objects.world.World())

        self.create_ui("hud")
        temp = self.get_ui("hud")
        hp_pos = (75,100)
        fr_pos = (75,300)
        super_diam_pos = (75,500)
        dmg_pos = (window_size.width-75,300)
        pi_pos = (window_size.width - 75, 100)
        spd_pos = (window_size.width-75,500)
        temp.new_img("hp_bg",importer.get_animated_sprite("health_indicator_hud")[0],hp_pos)
        temp.new_img("hp_indicator",importer.get_animated_sprite("health_indicator_hud")[1],hp_pos)
        temp.new_text_display("hp_amount",global_objects.get_font("text_font"),hp_pos)
        temp.get_text_display("hp_amount").set_all((255,255,255),45,"")
        temp.new_text_display("max_hp_amount",global_objects.get_font("text_font"),(hp_pos[0],hp_pos[1] + 60))
        temp.get_text_display("max_hp_amount").set_all((255,255,255),25,["Max HP: 000"])

        temp.new_img("firerate_bg",importer.get_animated_sprite("firerate_indicator_hud")[0],fr_pos)
        temp.new_img("firerate_indicator",importer.get_animated_sprite("firerate_indicator_hud")[1],fr_pos)
        temp.new_text_display("fr_amount",global_objects.get_font("text_font"),fr_pos)
        temp.get_text_display("fr_amount").set_all((255,255,255),45,"")

        temp.new_img("super_diamond_bg",importer.get_animated_sprite("super_indicator_hud")[0],super_diam_pos)
        temp.new_img("super_diamond",importer.get_animated_sprite("super_indicator_hud")[1],super_diam_pos)
        self.super_diamond_sprites = [importer.get_animated_sprite("super_indicator_hud")[1],importer.get_animated_sprite("super_indicator_hud")[2]]

        temp.new_img("dmg_drop",importer.get_sprite("damage_hud"),dmg_pos)
        temp.new_text_display("dmg_amount",global_objects.get_font("text_font"),(dmg_pos[0],dmg_pos[1]+ 20))
        temp.get_text_display("dmg_amount").set_all((255,255,255),45,"")

        temp.new_img("pierce_arrow",importer.get_sprite("pierce_hud"),pi_pos)
        temp.new_text_display("pierce_amount",global_objects.get_font("text_font"),pi_pos)
        temp.get_text_display("pierce_amount").set_all((255,255,255),45,"")

        temp.new_img("speed_bullet",importer.get_sprite("speed_hud"),spd_pos)
        temp.new_text_display("speed_amount",global_objects.get_font("text_font"),(spd_pos[0]+7,spd_pos[1]+4))
        temp.get_text_display("speed_amount").set_all((255,255,255),35,"")

        self.create_ui("boss_animation")
        ba_ui = self.get_ui("boss_animation")
        temp_img = pygame.Surface((900,600),SRCALPHA)
        temp_img.fill((0,0,0,64))
        ba_ui.new_img("bg",temp_img,gl_var.window_center)
        ba_ui.new_animation("boss_shake",importer.get_animated_sprite("boss_animation_vfx"),gl_var.window_center,10)
        ba_ui.new_text_display("wave_info",global_objects.get_font("title_font"),gl_var.window_center)
        ba_ui.get_text_display("wave_info").set_all((0,0,0),80,"")
        ba_ui.should_show = False

        self.create_ui("boss_hp")
        boss_hp_ui = self.get_ui("boss_hp")
        temp_img = pygame.Surface((400,40))
        temp_img.fill((0,0,0))
        pygame.draw.rect(temp_img,(255,0,0),(5,5,390,30))
        boss_hp_ui.new_img("boss_hp_indicator",temp_img,(gl_var.window_center[0],30))

        self.create_ui("pause")
        p_ui = self.get_ui("pause")
        temp_img = pygame.Surface((window_size.width,window_size.height),SRCALPHA)
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

        temp_img_import = importer.get_animated_sprite("super_indicator_hud")[1]
        self.super_diamond = pygame.Surface(temp_img_import.get_size(), SRCALPHA)
        self.super_percent = 1

        temp_img_import = importer.get_animated_sprite("health_indicator_hud")[1]
        self.hp_indicator = pygame.Surface(temp_img_import.get_size(),SRCALPHA)
        self.hp_indicator.blit(temp_img_import,(0,0))
        self.hp_percent = 1

        temp_img_import = importer.get_animated_sprite("firerate_indicator_hud")[1]
        self.fr_indicator = pygame.Surface(temp_img_import.get_size(),SRCALPHA)
        self.fr_indicator.blit(temp_img_import,(0,0))
        self.fr_percent = 1

        self.last_frame_hp = 0
        self.last_frame_max_hp = 0
        self.last_frame_fr = 0
        self.last_frame_dmg = 0
        self.last_frame_pi = 0
        self.last_frame_spd = 0
        self.last_frame_boss_hp = 0

        self.current_state = self.State.PLAYING
        self.upgrade_level = 0

        self.upgrader = Upgrader(global_objects)

    def _update(self, frame_data: FrameData):
        temp = self._objs[0]
        if isinstance(temp,World):
            if temp.upgrade[0]:
                self.current_state = self.State.UPGRADE
                self.upgrade_level = temp.upgrade[1]
        if self.current_state == self.State.UPGRADE:
            temp.game_paused = True
            if not self.upgrader.upgrades:
                self.upgrader.populate_upgrades(self.upgrade_level,temp.wave_count,temp.player.health,temp.player.max_health)
                self.upgrader.cooldown_on()
            else:
                self.upgrader.update(frame_data)
            if self.upgrader.should_end:
                self.upgrader.reset()
                self.current_state = self.State.PLAYING
                temp.resume_after_upgrade()

        temp_vfx = self.vfx_to_show[0]
        super()._update(frame_data)
        if self.current_state == self.State.PLAYING:
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
                self.super_diamond = self.super_diamond_sprites[1]
            else:
                self.super_diamond = self.super_diamond_sprites[0]
                self.super_diamond.set_alpha(255 * self.super_percent)

            if not temp.player.cooldown[2]:
                self.fr_percent = 1
            else:
                self.fr_percent = temp.player.cooldown[0] / temp.player.cooldown[1]

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
            self.get_ui("hud").get_img("super_diamond").change_img(self.super_diamond)
            self.get_ui("hud").get_img("hp_indicator").change_img(temp_b_img)

            temp_b_img =self.fr_indicator.copy()
            temp_b_img.set_alpha(255 * self.fr_percent)
            self.get_ui("hud").get_img("firerate_indicator").change_img(temp_b_img)

            if temp.player.health != self.last_frame_hp:
                self.last_frame_hp = temp.player.health
                self.get_ui("hud").get_text_display("hp_amount").set_text([f'{self.last_frame_hp}'])

            if temp.player.max_health != self.last_frame_max_hp:
                self.last_frame_max_hp = temp.player.max_health
                self.get_ui("hud").get_text_display("max_hp_amount").set_text([f'Max HP: {self.last_frame_max_hp}'])

            if temp.player.hud_firerate != self.last_frame_fr:
                self.last_frame_fr = temp.player.hud_firerate
                self.get_ui("hud").get_text_display("fr_amount").set_text([f'{self.last_frame_fr}x'])

            if temp.player.hud_dmg != self.last_frame_dmg:
                self.last_frame_dmg = temp.player.hud_dmg
                self.get_ui("hud").get_text_display("dmg_amount").set_text([f'{self.last_frame_dmg}'])

            if temp.player.pierce != self.last_frame_pi:
                self.last_frame_pi = temp.player.pierce
                self.get_ui("hud").get_text_display("pierce_amount").set_text([f'{self.last_frame_pi}'])

            if temp.player.hud_b_spd != self.last_frame_spd:
                self.last_frame_spd = temp.player.hud_b_spd
                self.get_ui("hud").get_text_display("speed_amount").set_text([f'{self.last_frame_spd}'])

            if temp.is_boss_wave:
                self.get_ui("boss_hp").should_show = True
                if self.last_frame_boss_hp != temp.combined_boss_hp:
                    self.last_frame_boss_hp = temp.combined_boss_hp
                    boos_hp_display_width = 390 * (temp.combined_boss_hp / temp.combined_boss_max_hp)
                    temp_img = pygame.Surface((400, 40))
                    temp_img.fill((0, 0, 0))
                    pygame.draw.rect(temp_img, (255, 0, 0), (5, 5, boos_hp_display_width, 30))
                    self.get_ui("boss_hp").get_img("boss_hp_indicator").change_img(temp_img)
            else:
                self.get_ui("boss_hp").should_show = False


    def _draw(self,surface: pygame.Surface):
        super()._draw(surface)
        if self.current_state == self.State.UPGRADE:
            self.upgrader.draw(surface)

    def on_changed_to(self,previous_scene_id):
        self._objs[0].reset()