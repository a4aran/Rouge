import random

import pygame
from pygame import SRCALPHA

from current_game_run_data import cur_run_data
from Illusion.frame_data_f import FrameData
from ar_math_helper import angle_to_mouse
from c_objects.entities.entity import Entity
from c_objects.entities.projectiles import PierceProj, FreezePP
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from c_objects.world import World


class Player(Entity):
    def __init__(self):
        super().__init__(pygame.Vector2(270,270),15)
        self.speed = 120
        self.base_fire_cooldown = 0.5
        self.firerate = 1
        self.cooldown = [0,self.base_fire_cooldown / self.firerate,False]
        self.id = "Player"
        self.max_health = 100
        self.health = self.max_health
        self.super = {
            "name": "dash",
            "cooldown": [0,3,True],
            "active": [0,0.5,False]
        }
        self.attack_damage = 10
        self.pierce = 1
        self.b_speed = 170

        self.bullet_counter = 0

        self.hud_firerate = self.firerate
        self.hud_dmg = self.attack_damage
        self.hud_b_spd = self.b_speed

        self.autofire_kc = False
        self.autofire = False

        self.multipliers = {
            "firerate": 1,
            "damage": 1,
            "bullet_speed": 1
        }

        self.on_death = {"shoot": False}

    def update(self,world: "World",frame_data: FrameData):
        self.multipliers = {
            "firerate": 1,
            "damage": 1,
            "bullet_speed": 1
        }
        if cur_run_data.request_player_upgrade:
            temp = cur_run_data.active_upgrades
            self.attack_damage = 10 + temp[0]["damage"]
            self.pierce = 1 + temp[0]["pierce"]
            self.b_speed = 170 + temp[0]["bullet_speed"]
            self.firerate = 1 + temp[0]["firerate"]
        for lvl_2 in cur_run_data.active_upgrades[1]:
            if lvl_2 != "double_trouble":
                if cur_run_data.active_upgrades[1][lvl_2][0]:
                    self.multipliers[cur_run_data.active_upgrades[1][lvl_2][2]] += cur_run_data.active_upgrades[1][lvl_2][3]
        for kind in self.multipliers:
            self.multipliers[kind] = max(0.2,self.multipliers[kind])

        self.on_death["shoot"] = cur_run_data.active_upgrades[2]["shoot_on_death"][0]
        print(world.deleted_entities_amount)
        if cur_run_data.active_upgrades[2]["lifesteal"][0]:
            if world.deleted_entities_amount > 0:
                for i in range(world.deleted_entities_amount):
                    if cur_run_data.get_random_chance(cur_run_data.active_upgrades[2]["lifesteal"][1]):
                        cur_run_data.heal_q += 1

        if cur_run_data.heal_q != 0:
            self.health += cur_run_data.heal_q
            self.health = min(self.max_health,self.health)
            cur_run_data.heal_q = 0

        self.max_health = 100 + cur_run_data.add_max_hp

        loc_speed = self.speed
        loc_firerate = self.firerate
        if self.super["active"][2]:
            loc_speed *= 2
            loc_firerate += 1.5
            loc_firerate = round(loc_firerate,2)
            self.super["active"][0] += frame_data.dt
            if self.super["active"][0] > self.super["active"][1]:
                self.super["active"][2] = False
                self.super["active"][0] = 0
        self.update_shooting_cooldown(loc_firerate)

        loc_firerate = round(loc_firerate * self.multipliers["firerate"],2)
        loc_dmg = round(self.attack_damage * self.multipliers["damage"],1)
        loc_b_spd = round(self.b_speed * self.multipliers["bullet_speed"],1)

        loc_firerate += cur_run_data.get_PA_additional_fr(loc_b_spd)
        loc_dmg += cur_run_data.get_blitz_additional_dmg(loc_firerate)
        loc_b_spd += 0

        loc_firerate =round(loc_firerate,2)
        loc_dmg = round(loc_dmg,1)
        loc_b_spd = round(loc_b_spd,1)

        self.hud_firerate = round(loc_firerate,2)
        self.hud_dmg = round(loc_dmg)
        self.hud_b_spd = round(loc_b_spd)

        direction = pygame.Vector2(0, 0)

        if frame_data.keys[pygame.K_w]:
            direction.y -= 1
        if frame_data.keys[pygame.K_s]:
            direction.y += 1
        if frame_data.keys[pygame.K_a]:
            direction.x -= 1
        if frame_data.keys[pygame.K_d]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        velocity = direction * loc_speed * frame_data.dt

        self.hitbox.pos += velocity

        if frame_data.keys[pygame.K_f] and not self.autofire_kc:
            self.autofire = not  self.autofire

        self.autofire_kc = frame_data.keys[pygame.K_f]

        if self.cooldown[2]:
            self.cooldown[0] += frame_data.dt
            if self.cooldown[0] >= self.cooldown[1]:
                self.cooldown[0] = 0
                self.cooldown[2] = False

        if (frame_data.mouse_buttons[0] or self.autofire) and not self.cooldown[2]:
            angles = [angle_to_mouse(self.hitbox.pos + world.offset)]
            data = cur_run_data.get_second_lvl("triple_shot")
            if data[0]:
                if cur_run_data.get_random_chance(data[1]):
                    angles.append((angles[0] + 30) % 360)
                    angles.append((angles[0] + 330) % 360)
            self.bullet_counter += 1

            data = cur_run_data.get_second_lvl("freezing_b")
            b_shot = False

            for ang in angles:
                if data[0]:
                    if self.bullet_counter % data[1] == 0:
                        self.shoot(world,"freeze",ang,loc_dmg,loc_b_spd)
                        b_shot = True
                if not b_shot:
                    self.shoot(world, "normal", ang, loc_dmg, loc_b_spd)
            self.cooldown[2] = True

        if not self.super["cooldown"][2]:
            self.super["cooldown"][0] += frame_data.dt
            if self.super["cooldown"][0] >= self.super["cooldown"][1]:
                self.super["cooldown"][0] = 0
                self.super["cooldown"][2] = True

        if self.super["cooldown"][2] and frame_data.mouse_buttons[2] and not self.super["active"][2]:
            self.super["active"][2] = True
            self.super["cooldown"][2] = False

        self.clamp_pos(world.w_size)

    def shoot(self,world: "World",type: str,angle,dmg: float, b_spd: float):
        bc = 0
        if cur_run_data.active_upgrades[1]["bounce"][0]:
            bc = cur_run_data.active_upgrades[1]["bounce"][1]
        if type == "normal":
            world.projectiles.append(PierceProj(
                pygame.Vector2(self.hitbox.radius, 0)
                .rotate(angle) + self.hitbox.pos, angle, dmg,
                b_spd, self.pierce,bc,self.on_death))
        elif type == "freeze":
            world.projectiles.append(FreezePP(
                pygame.Vector2(self.hitbox.radius, 0)
                .rotate(angle) + self.hitbox.pos, angle, dmg,
                b_spd, self.pierce,bc,self.on_death))

    def shoot_custom(self,world: "World",type: str,angle,pos: pygame.Vector2):
        dmg, b_spd = self.bullet_stats_provider()
        bc = 0
        if cur_run_data.active_upgrades[1]["bounce"][0]:
            bc = cur_run_data.active_upgrades[1]["bounce"][1]
        if type == "normal":
            world.projectiles.append(PierceProj(
                pos, angle, dmg,
                b_spd, self.pierce,bc,self.on_death))
        elif type == "freeze":
            world.projectiles.append(FreezePP(
                pos, angle, dmg,
                b_spd, self.pierce,bc,self.on_death))

    def bullet_stats_provider(self):
        self.multipliers = {
            "firerate": 1,
            "damage": 1,
            "bullet_speed": 1
        }
        for lvl_2 in cur_run_data.active_upgrades[1]:
            if lvl_2 != "double_trouble":
                if cur_run_data.active_upgrades[1][lvl_2][0]:
                    self.multipliers[cur_run_data.active_upgrades[1][lvl_2][2]] += cur_run_data.active_upgrades[1][lvl_2][3]
        for kind in self.multipliers:
            self.multipliers[kind] = max(0.2,self.multipliers[kind])
        loc_dmg = round(self.attack_damage * self.multipliers["damage"],1)
        loc_b_spd = round(self.b_speed * self.multipliers["bullet_speed"],1)
        return loc_dmg,loc_b_spd

    def update_shooting_cooldown(self,fire_rate):
        self.cooldown[1] = self.base_fire_cooldown / fire_rate

    def damage(self,damager: Entity,amount: int):
        if hasattr(damager,"damage_on_touch"):
            damager.should_delete = True
        self.health -= amount

    def reset(self):
        self.attack_damage = 10
        self.pierce = 1
        self.b_speed = 170
        self.max_health = 100
        self.health = self.max_health
        self.firerate = 1
        self.autofire_kc =[0,0.1,False]
        self.autofire = False

    def reset_cooldowns(self):
        self.cooldown[0] = 0
        self.cooldown[2] = False

        self.super = {
            "name": "dash",
            "cooldown": [0,3,True],
            "active": [0,0.5,False]
        }