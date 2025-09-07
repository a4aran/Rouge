import copy
import random

import pygame
from pygame import SRCALPHA

import ar_math_helper
import gl_var
from Illusion.frame_data_f import FrameData
from c_objects.entities import projectiles
from c_objects.entities.entity import Entity


class Enemy(Entity):
    def __init__(self, pos: pygame.Vector2, hitbox_radius: float,health: float,speed: float,dmg: float = 10):
        super().__init__(pos, hitbox_radius)
        self.health = health
        self.speed = speed
        self.color = (255,255,0)
        self.status_effects = copy.deepcopy(gl_var.status_effect)
        self.atk_dmg = dmg
        self.a_atk_dmg = dmg

    def damage(self,amount: float,effects: list = False):
        self.health -= amount
        if self.health <= 0:
            self.should_delete = True
            return
        if effects:
            for ef in effects:
                if ef[0] == "freeze":
                    self.apply_freeze(ef[1])
        self.trigger_flash()

    def apply_freeze(self,time: float):
        self.status_effects["time"]["freeze"][0] = 0
        self.status_effects["time"]["freeze"][1] = time
        self.status_effects["time"]["freeze"][2] = True

    def update_status_effects(self,fd: FrameData):
        for effect in self.status_effects["time"]:
            data = self.status_effects["time"][effect]
            if data[2]:
                data[0] += fd.dt
                if data[0] >= data[1]:
                    data[0] = 0
                    data[1] = 0
                    data[2] = False

    def get_local_vars(self):
        locs = [self.speed,self.atk_dmg]
        if self.status_effects["time"]["freeze"][2]: locs[0] = 0
        return locs

    def draw_effects(self):
        cent = (self.hitbox.radius*2,self.hitbox.radius*2)
        surf = pygame.Surface((self.hitbox.radius*4,self.hitbox.radius*4),SRCALPHA)

        if self.status_effects["time"]["freeze"][2]:
            pygame.draw.circle(surf,(100,255,255,100),cent,self.hitbox.radius*1.5)

        return surf

    def draw(self,surf: pygame.Surface,offset: pygame.Vector2):
        surf.blit(self.draw_effects(),self.hitbox.pos + offset + pygame.Vector2(self.hitbox.radius * -2,self.hitbox.radius * -2))
        super().draw(surf,offset)

class SimpleAIEnemy(Enemy):
    def __init__(self, pos: pygame.Vector2,health = 50,spd = 50,cooldown = 0.2,length_range: tuple[int,int] = (50,130)):
        super().__init__(pos, 12.5, health, spd)
        self.direction = None
        self.cooldown = [cooldown * 0.7,cooldown,True]
        self.length = 0
        self.length_range = length_range
        self.damage_on_touch = True
        self.outline_color = (255,0,0)

    def update(self,world: "World",frame_data: FrameData):
        self.update_status_effects(frame_data)
        loc_speed,self.a_atk_dmg = self.get_local_vars()
        self.flash_countdown(frame_data.dt)
        if not self.cooldown[2] and self.direction is None:
            self.randomize_goal(world.w_size,world.boss,world.player)
        if self.direction is not None and self.length > 0:
            vel = pygame.Vector2(1,0).rotate(self.direction).normalize() * loc_speed * frame_data.dt
            self.hitbox.pos += vel
            self.length -= vel.length()
        if self.length <= 0:
            self.direction = None
            self.cooldown[2] = True
        if self.cooldown[2]:
            self.cooldown[0] += frame_data.dt
            if self.cooldown[0] > self.cooldown[1]:
                self.cooldown[0] = 0
                self.cooldown[2] = False
        self.clamp_pos(world.w_size)

    def randomize_goal(self,clamp_size: tuple[int, int],boss,player):
        self.direction = random.randint(0, 359)
        self.length = random.randint(self.length_range[0], self.length_range[1])

        eta = pygame.Vector2(50,0).rotate(self.direction).normalize() + self.hitbox.pos
        radius = self.hitbox.radius
        x, y = eta
        if (x < 0 + radius or x > clamp_size[0] - radius or
                y < 0 + radius or y > clamp_size[1] - radius):
            self.direction =  ar_math_helper.angle_to_target(self.hitbox.pos,player.hitbox.pos)
            print("to player")
        if boss:
            for b in boss:
                if isinstance(b,Entity) and b.hitbox.line_circle_collision(self.hitbox.pos,eta):
                    self.direction =  ar_math_helper.angle_to_target(self.hitbox.pos,player.hitbox.pos)
                    print("to player")

    def clamp_pos(self, clamp_size: tuple[int, int]):
        radius = self.hitbox.radius
        x, y = self.hitbox.pos

        if (x < 0 + radius or x > clamp_size[0] - radius or
                y < 0 + radius or y > clamp_size[1] - radius):
            self.direction = None
            self.cooldown[0] = self.cooldown[1] * 0.5
            self.cooldown[2] = True
        self.hitbox.pos.x = min(max(0 + radius,self.hitbox.pos.x),clamp_size[0] - radius)
        self.hitbox.pos.y = min(max(0 + radius,self.hitbox.pos.y),clamp_size[1] - radius)

    def draw(self,surf: pygame.Surface,offset: pygame.Vector2):
        super().draw(surf,offset)
        # if self.direction is not  None:
        #     vec = pygame.Vector2(1,0).rotate(self.direction).normalize() * 100
        #     vec = vec + self.hitbox.pos + offset
        #     pygame.draw.line(surf,(255,0,0),self.hitbox.pos+offset,vec,4)

class FasterSAiEnemy(SimpleAIEnemy):
    def __init__(self, pos: pygame.Vector2,health = 50,spd=30,speed_mult = 1.2):
        super().__init__(pos,health=health,spd=spd,cooldown=0.5,length_range=(130,250))
        self.add_speed = self.speed
        self.spd_mult = speed_mult
        self.color = (255,150,0)

    def update(self,world: "World",frame_data: FrameData):
        self.speed = self.length * self.spd_mult + self.add_speed
        super().update(world,frame_data)

class DoubleSAiEnemy(SimpleAIEnemy):
    def __init__(self, pos: pygame.Vector2,health = 50,spd = 50,cooldown = 0.2,length_range: tuple[int,int] = (50,130)):
        super().__init__(pos,health,spd,cooldown,length_range)
        self.previous_dir = 0
        self.color = (0,0,0)
        self.other_goal_chance = 0.5
        self.atk_dmg = 15

    def update(self, world: "World", frame_data: FrameData):
        self.update_status_effects(frame_data)
        loc_speed, self.a_atk_dmg = self.get_local_vars()
        self.flash_countdown(frame_data.dt)
        if not self.cooldown[2] and self.direction is None:
            self.roll_randomize_goal(world)
        if self.direction is not None and self.length > 0:
            vel = pygame.Vector2(1, 0).rotate(self.direction).normalize() * loc_speed * frame_data.dt
            self.hitbox.pos += vel
            self.length -= vel.length()
        if self.length <= 0:
            self.direction = None
            self.cooldown[2] = True
        if self.cooldown[2]:
            self.cooldown[0] += frame_data.dt
            if self.cooldown[0] > self.cooldown[1]:
                self.cooldown[0] = 0
                self.cooldown[2] = False
        self.clamp_pos(world.w_size)
        if self.direction is not  None:
            self.previous_dir = self.direction

    def roll_randomize_goal(self,world: "World"):
        if random.random() < self.other_goal_chance:
            self.randomize_goal(world.w_size,world.boss,world.player)
        else:
            self.other_goal_randomizer(world)

    def other_goal_randomizer(self,world: "World"):
        loc_dir = self.previous_dir
        if loc_dir is None:
            loc_dir = 0
        loc_dir = (loc_dir + 180) % 360
        self.direction = loc_dir
        self.length = random.randint(self.length_range[0],self.length_range[1])
        eta = pygame.Vector2(50,0).rotate(self.direction).normalize() + self.hitbox.pos
        radius = self.hitbox.radius
        x, y = eta
        clamp_size = world.w_size
        if (x < 0 + radius or x > clamp_size[0] - radius or
                y < 0 + radius or y > clamp_size[1] - radius):
            self.direction = random.randint(0, 359)
            self.length = random.randint(50, 90)

class ShootingEnemy(SimpleAIEnemy):
    def __init__(self, pos: pygame.Vector2,health = 50,spd = 50):
        super().__init__(pos,health=health,spd=spd)
        self.shooting_cooldown = [0,1.25]
        self.color = (0,255,0)
        self.outline_color = (0,0,0)
        self.damage_on_touch = False

    def update(self,world: "World",frame_data: FrameData):
        super().update(world,frame_data)
        self.shooting_cooldown[0] += frame_data.dt
        if self.shooting_cooldown[0] >= self.shooting_cooldown[1]:
            self.shooting_cooldown[0] = 0

            ang = self.hitbox.pos.angle_to(world.player.hitbox.pos) if random.random() < 0.1 else random.randint(0,360)

            world.enemy_projectiles.append(projectiles.EnemyProj(self.hitbox.pos.copy(),ang,100,4))