import random
from random import choices

import pygame
from pygame import SRCALPHA

from current_game_run_data import cur_run_data
import gl_var
import window_size
from Illusion.frame_data_f import FrameData
from Illusion.go import GlobalObjects
from Illusion.helper import c_helper
from Illusion.ui import UI
from ar_math_helper import formulas

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
        self.up_poses = [(150,50),(150,350)]
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
        def __init__(self,level,pos,wave,add_heal,exclude_up = None):
            self.level = level
            self.kind = self.roll_upgrade_kind(exclude_up,add_heal)
            self.stats = self.get_stats(wave)
            self.hoverbox = pygame.Rect(pos,(600,200))
            self.is_hovered = False

        def roll_upgrade_kind(self, exclude, add_heal: bool):
            if self.level == 1:
                temp_lvl_4 = cur_run_data.get_lvl_3_active_upgrades()
                if temp_lvl_4 is not None:
                    temp_lvl_4 = [k for k in temp_lvl_4 if k not in exclude]
                if temp_lvl_4 is not None and temp_lvl_4:
                    self.level = 4 if random.random() > 0.6 else 1
                if self.level == 1:
                    choices = gl_var.level_1_upgrade_list.copy()
                    if add_heal and exclude != "heal": choices.append("heal")
                    if exclude is not None:
                        # handle list or single string
                        if isinstance(exclude, list):
                            for ex in exclude:
                                if ex != "heal" and ex in choices:
                                    choices.remove(ex)
                        elif exclude != "heal" and exclude in choices:
                            choices.remove(exclude)
                    return random.choice(choices)
                else:
                    choices = cur_run_data.get_lvl_3_active_upgrades()
                    if exclude:
                        if isinstance(exclude, list):
                            for ex in exclude:
                                if ex in choices:
                                    choices.remove(ex)
                        elif exclude in choices:
                            choices.remove(exclude)
                    return random.choice(choices) + "_up"
            elif self.level == 2:
                choices = gl_var.level_2_upgrade_list.copy()
                if exclude:
                    if isinstance(exclude, list):
                        for ex in exclude:
                            if ex in choices:
                                choices.remove(ex)
                    elif exclude in choices:
                        choices.remove(exclude)
                return random.choice(choices)
            elif self.level == 3:
                choices = gl_var.level_3_upgrade_list.copy()
                if exclude:
                    if isinstance(exclude, list):
                        for ex in exclude:
                            if ex in choices:
                                choices.remove(ex)
                    elif exclude in choices:
                        choices.remove(exclude)
                return random.choice(choices)
        def get_stats(self,wave):
            r = random.randint(70,125) / 100
            temp = []
            if self.level == 1:
                if self.kind == "damage":
                    temp.append(formulas.damage_upgrade(wave))
                elif self.kind == "pierce":
                    temp.append(1)
                elif self.kind == "bullet_speed":
                    temp.append(formulas.b_speed_upgrade(wave))
                elif self.kind == "firerate":
                    temp.append(formulas.firerate_upgrade(wave))
                elif self.kind == "heal":
                    temp.append(10)
            if self.level == 2:
                if self.kind == "freezing_b":
                    temp.append(cur_run_data.active_upgrades[1]["freezing_b"][1])
                    temp.append(round(cur_run_data.active_upgrades[1]["freezing_b"][3] * 100))
                elif self.kind == "triple_shot":
                    temp.append(round(cur_run_data.active_upgrades[1]["triple_shot"][1] * 100 * cur_run_data.chance_mult()))
                    temp.append(round(cur_run_data.active_upgrades[1]["triple_shot"][3] * 100))
                elif self.kind == "bounce":
                    temp.append(round(cur_run_data.active_upgrades[1]["bounce"][1] * 100 * cur_run_data.chance_mult()))
                    temp.append(round(cur_run_data.active_upgrades[1]["bounce"][3] * 100))
                elif self.kind == "double_trouble":
                    temp.append("")
            if self.level == 3:
                if self.kind == "shoot_on_death":
                    temp.append(cur_run_data.active_upgrades[2]["shoot_on_death"][1])
                    temp.append(cur_run_data.active_upgrades[2]["shoot_on_death"][2])
            if self.level == 4:
                if self.kind == "shoot_on_death_up":
                    temp.append(cur_run_data.active_upgrades[3]["shoot_on_death_up"])
                    temp.append(cur_run_data.active_upgrades[2]["shoot_on_death"][1])
                    temp.append(cur_run_data.active_upgrades[2]["shoot_on_death"][2])
            return temp


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
                    cur_run_data.active_upgrades[self.picked.level-1][self.picked.kind] += self.picked.stats[0]
                    cur_run_data.round_active_upgrades()
                    cur_run_data.request_player_upgrade = True
                    self.should_end = True
            elif self.picked.level == 2:
                cur_run_data.active_upgrades[self.picked.level - 1][self.picked.kind][0] = True
                cur_run_data.round_active_upgrades()
                cur_run_data.request_player_upgrade = True
                self.should_end = True
            elif self.picked.level == 3:
                cur_run_data.active_upgrades[self.picked.level - 1][self.picked.kind][0] = True
                cur_run_data.round_active_upgrades()
                cur_run_data.request_player_upgrade = True
                self.should_end = True
            if self.picked.level == 4:
                cur_run_data.active_upgrades[self.picked.level - 2][self.picked.kind.removesuffix("_up")][1] += cur_run_data.active_upgrades[3]["shoot_on_death_up"]
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

        r = random.randint(100,140)
        r /= 100
        ah = player_hp < (player_max_hp * r)/2

        self.upgrades = []
        self.upgrades.append(self._Upgrade(level,self.up_poses[0],wave,ah,true_amount))
        temp = self.compiler.get_compiled_text(self.upgrades[0].level,self.upgrades[0].kind,self.upgrades[0].stats)
        self.ui.get_text_display("up_1_title").set_size(45 if len(temp[0][0]) < 15 else 35)
        self.ui.get_text_display("up_1_title").set_text(temp[0])
        self.ui.get_text_display("up_1_text").set_text(temp[1])

        self.upgrades.append(self._Upgrade(level,self.up_poses[1],wave,ah,exc))
        temp = self.compiler.get_compiled_text(self.upgrades[1].level,self.upgrades[1].kind,self.upgrades[1].stats)
        self.ui.get_text_display("up_2_title").set_size(45 if len(temp[0][0]) < 15 else 35)
        self.ui.get_text_display("up_2_title").set_text(temp[0])
        self.ui.get_text_display("up_2_text").set_text(temp[1])

        print(cur_run_data.active_upgrades)

    def check_level_2(self,level,true_amount: list):
        up_to_choose = 2
        for kind in cur_run_data.active_upgrades[1]:
            if cur_run_data.active_upgrades[1][kind][0]: true_amount.append(kind)
        if len(true_amount) == len(cur_run_data.active_upgrades[1]): level = 1
        if not (abs(len(cur_run_data.active_upgrades[1]) - len(true_amount)) > 1):
            up_to_choose = 1
        return level,up_to_choose

    def check_level_3(self,level,true_amount: list):
        up_to_choose = 2
        level = level
        for kind in cur_run_data.active_upgrades[2]:
            if cur_run_data.active_upgrades[2][kind][0]: true_amount.append(kind)
        if len(true_amount) == len(cur_run_data.active_upgrades[2]): level = 2
        if not (abs(len(cur_run_data.active_upgrades[2]) - len(true_amount)) > 1):
            up_to_choose = 1
        return level,up_to_choose

    def check_levels(self,level,true_amount):
        temp_list = []
        up_to_choose = 2
        level = level
        if level == 2: level,up_to_choose = self.check_level_2(level,temp_list)
        elif level == 3:
            level, up_to_choose = self.check_level_3(level, temp_list)
            if level == 2:
                temp_list.clear()
                level, up_to_choose = self.check_level_2(level, temp_list)
        true_amount = temp_list.copy()
        return level,up_to_choose

    def construct_available_upgrades_list(self,add_heal:bool):
        level_1 = gl_var.level_1_upgrade_list.copy()
        if add_heal: level_1.append("heal")
        level_2 = []
        for kind in cur_run_data.active_upgrades[1]:
            if cur_run_data.get_second_lvl(kind): level_2.append(kind)
        level_3 = cur_run_data.get_lvl_3_active_upgrades()
        return level_1,level_2,level_3

    def cooldown_on(self):
        self.pop_up_cooldown[2] = True