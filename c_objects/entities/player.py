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

        self.autofire_kc = False
        self.autofire = False

    def update(self,world: "World",frame_data: FrameData):
        if cur_run_data.request_player_upgrade:
            temp = cur_run_data.active_upgrades
            self.attack_damage = 10 + temp[0]["damage"]
            self.pierce = 1 + temp[0]["pierce"]
            self.b_speed = 170 + temp[0]["bullet_speed"]
            self.firerate = 1 + temp[0]["firerate"]
        if cur_run_data.heal_q != 0:
            self.health += cur_run_data.heal_q
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
        loc_firerate = round(loc_firerate,2)
        self.hud_firerate = loc_firerate

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
                        world.projectiles.append(FreezePP(
                            pygame.Vector2(self.hitbox.radius, 0)
                            .rotate(ang) + self.hitbox.pos, ang, self.attack_damage,
                            self.b_speed, self.pierce))
                        b_shot = True
                if not b_shot:
                    world.projectiles.append(PierceProj(
                    pygame.Vector2(self.hitbox.radius,0)
                    .rotate(ang) + self.hitbox.pos,ang,self.attack_damage,
                    self.b_speed,self.pierce))

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

    def shoot(self,world: "World",type: str,angle):
        if type == "normal":
            world.projectiles.append(PierceProj(
                pygame.Vector2(self.hitbox.radius, 0)
                .rotate(angle) + self.hitbox.pos, angle, self.attack_damage,
                self.b_speed, self.pierce))
        elif type == "freeze":
            world.projectiles.append(FreezePP(
                pygame.Vector2(self.hitbox.radius, 0)
                .rotate(angle) + self.hitbox.pos, angle, self.attack_damage,
                self.b_speed, self.pierce))

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