import random
from random import choices

import pygame
from pygame import SRCALPHA

import upgrades_data
from current_game_run_data import cur_run_data
import gl_var
import window_size
from Illusion.frame_data_f import FrameData
from Illusion.go import GlobalObjects
from Illusion.helper import c_helper
from Illusion.ui import UI
from ar_math_helper import formulas
from characters import characters as chars

from description_compiler import DescCompiler


class Upgrader:
    def __init__(self,go: GlobalObjects):
        self.sprites = [
            go.get_custom_object("heart_up"),
            go.get_custom_object("level_1_up"),
            go.get_custom_object("level_2_up"),
            go.get_custom_object("level_3_up"),
            go.get_custom_object("level_4_up")
        ]
        self.upgrades = []
        self.picked = None
        self.should_end = False
        self.level = 0
        self.active = False

        self.pop_up_cooldown = [0,1,False]

        self.compiler = DescCompiler()
        self.ui = UI("def")
        self.up_poses = [(150,gl_var.window_center[1]-230),(150,gl_var.window_center[1]+30)]
        self.ui.new_text_display("up_1_title",go.get_font("title_font"),(gl_var.window_center[0],0))
        temp = self.ui.get_text_display("up_1_title")
        temp.set_all((0,0,0),45,["example title"])
        temp.toggle_constant_y_pos()
        temp.set_constant_y_pos(self.up_poses[0][1]+10)

        self.ui.new_text_display("up_1_text",go.get_font("text_font"),(gl_var.window_center[0],0))
        temp = self.ui.get_text_display("up_1_text")
        temp.set_all((0,0,0),30,["example","text","can","have"])
        temp.toggle_constant_y_pos()
        temp.set_constant_y_pos(self.up_poses[0][1]+60)

        self.ui.new_text_display("up_2_title",go.get_font("title_font"),(gl_var.window_center[0],0))
        temp = self.ui.get_text_display("up_2_title")
        temp.set_all((0,0,0),45,["example title"])
        temp.toggle_constant_y_pos()
        temp.set_constant_y_pos(self.up_poses[1][1]+10)

        self.ui.new_text_display("up_2_text",go.get_font("text_font"),(gl_var.window_center[0],0))
        temp = self.ui.get_text_display("up_2_text")
        temp.set_all((0,0,0),30,["example","text","can","have"])
        temp.toggle_constant_y_pos()
        temp.set_constant_y_pos(self.up_poses[1][1]+60)


    class _Upgrade(c_helper.Hoverable):
        def __init__(self,level,pos,wave,upgrades_list):
            self.level = level
            self.kind = self.roll_upgrade_kind(upgrades_list)
            self.stats = self.get_stats(wave)
            self.hoverbox = pygame.Rect(pos,(600,200))
            self.is_hovered = False

        def roll_upgrade_kind(self, possible_upgrades_list: list[list,list,list,list]):
            if self.level == 1 and possible_upgrades_list[3]:
                self.level = 4 if random.random() < 0.3 else 1
            if self.level == 2 and possible_upgrades_list[3]:
                self.level = 4 if random.random() < 0.6 else 2
            return random.choice(possible_upgrades_list[self.level - 1])

        def get_stats(self, wave):
            level = self.level - 1  # convert 1-based to 0-based index
            kind = self.kind
            context = cur_run_data.get_context()

            upgrades = [
                upgrades_data.lvl1,
                upgrades_data.lvl2,
                upgrades_data.lvl3,
                upgrades_data.lvl4
            ]
            if kind != "heal":
                data = upgrades[level].get(kind)
                if data is None:
                    return []
            else:
                data = [10]

            fn = cur_run_data.stats[level].get(kind)
            if fn is None:
                return []

            # some of your lvl3 definitions use [lambda], fix that
            if isinstance(fn, list):
                return [f(data, wave, context, upgrades) for f in fn]

            return fn(data, wave, context, upgrades)

    def update(self,fd: FrameData):
        click = fd.mouse_buttons[0]
        if self.pop_up_cooldown[2]:
            click = False
            self.pop_up_cooldown[0] += fd.dt
            if self.pop_up_cooldown[0] > self.pop_up_cooldown[1]:
                self.pop_up_cooldown[0] = 0
                self.pop_up_cooldown[2] = False
        if self.upgrades:
            for up in self.upgrades:
                if isinstance(up,self._Upgrade):
                    up.is_hovered = up.check_hovers(fd)
                    if up.is_hovered and click:
                        self.picked = up
        if self.picked is not None:
            if self.picked.level == 1:
                if self.picked.kind == "heal":
                    cur_run_data.heal_q = 10
                    self.should_end = True
                else:
                    cur_run_data.active_stats[self.picked.level - 1][self.picked.kind] += self.picked.stats[0]
                    cur_run_data.round_active_upgrades()
                    cur_run_data.request_player_upgrade = True
                    self.should_end = True
            elif self.picked.level == 2:
                cur_run_data.active_stats[self.picked.level - 1][self.picked.kind] = True
                cur_run_data.round_active_upgrades()
                cur_run_data.request_player_upgrade = True
                self.should_end = True
            elif self.picked.level == 3:
                cur_run_data.active_stats[self.picked.level - 1][self.picked.kind + "_bool"] = True
                cur_run_data.round_active_upgrades()
                cur_run_data.request_player_upgrade = True
                self.should_end = True
            if self.picked.level == 4:
                cur_run_data.active_stats[self.picked.level - 2][self.picked.kind.removesuffix("_up") + "_value"] += upgrades_data.lvl4[self.picked.kind]
                cur_run_data.round_active_upgrades()
                cur_run_data.request_player_upgrade = True
                self.should_end = True
        self.ui.update(fd)

    def draw(self,surface: pygame.Surface):
        temp = pygame.Surface((window_size.width,window_size.height),SRCALPHA)
        temp.fill((0,0,0,128))
        surface.blit(temp,(0,0))

        for up in self.upgrades:
            if isinstance(up, self._Upgrade):
                if up.kind != "heal":
                    if up.is_hovered:
                        surface.blit(self.sprites[up.level][1],up.hoverbox.topleft)
                    else:
                        surface.blit(self.sprites[up.level][0],up.hoverbox.topleft)
                else:
                    if up.is_hovered:
                        surface.blit(self.sprites[0][1],up.hoverbox.topleft)
                    else:
                        surface.blit(self.sprites[0][0],up.hoverbox.topleft)
        self.ui.draw(surface)

    def reset(self):
        self.upgrades = []
        self.picked = None
        self.should_end = False

    def populate_upgrades(self,level,wave,player_hp,player_max_hp):
        upgrade_list = self.construct_available_upgrades_list(
            player_hp < (player_max_hp * (random.randint(100,140) / 100))/2)
        if level == 2 and len(upgrade_list[1]) == 0: level = 1
        if level == 3 and len(upgrade_list[2]) == 0:
            level = 2
            if len(upgrade_list[1]) == 0: level = 1


        self.upgrades = []
        self.upgrades.append(self._Upgrade(level,self.up_poses[0],wave,upgrade_list))
        temp = self.compiler.get_compiled_text(self.upgrades[0].level,self.upgrades[0].kind,self.upgrades[0].stats)
        self.ui.get_text_display("up_1_title").set_size(45 if len(temp[0][0]) < 15 else 35)
        self.ui.get_text_display("up_1_title").set_text(temp[0])
        self.ui.get_text_display("up_1_text").set_text(temp[1])

        upgrade_list[self.upgrades[0].level - 1].remove(self.upgrades[0].kind)
        if self.upgrades[0].level == 4:
            upgrade_list[3] = []
        if level == 2 and len(upgrade_list[1]) == 0: level = 1
        if level == 3 and len(upgrade_list[2]) == 0:
            level = 2
            if len(upgrade_list[1]) == 0: level = 1

        self.upgrades.append(self._Upgrade(level,self.up_poses[1],wave,upgrade_list))
        temp = self.compiler.get_compiled_text(self.upgrades[1].level,self.upgrades[1].kind,self.upgrades[1].stats)
        self.ui.get_text_display("up_2_title").set_size(45 if len(temp[0][0]) < 15 else 35)
        self.ui.get_text_display("up_2_title").set_text(temp[0])
        self.ui.get_text_display("up_2_text").set_text(temp[1])

    def construct_available_upgrades_list(self,add_heal:bool):
        level_1 = gl_var.level_1_upgrade_list.copy()
        level_1.append(chars[cur_run_data.selected_character]["upgradable_stat"])
        if add_heal: level_1.append("heal")
        level_2 = []
        for kind in cur_run_data.active_stats[1]:
            if not cur_run_data.get_second_lvl(kind): level_2.append(kind)
        level_3 = []
        for kind in upgrades_data.lvl3:
            if not cur_run_data.active_stats[2][kind + "_bool"]: level_3.append(kind)
        level_4 = []
        for name in cur_run_data.get_lvl_3_active_upgrades():
            level_4.append(name + "_up")
        return [level_1,level_2,level_3,level_4]

    def cooldown_on(self):
        self.pop_up_cooldown[2] = True