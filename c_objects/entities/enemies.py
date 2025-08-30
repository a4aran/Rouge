import random

import pygame

from Illusion.frame_data_f import FrameData
from c_objects.entities.entity import Entity


class Enemy(Entity):
    def __init__(self, pos: pygame.Vector2, hitbox_radius: float,health: float,speed: float):
        super().__init__(pos, hitbox_radius)
        self.health = health
        self.speed = speed
        self.color = (255,255,0)

    def damage(self,amount: float):
        self.health -= amount
        if self.health <= 0: self.should_delete = True
        self.trigger_flash()

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
        self.flash_countdown(frame_data.dt)
        if not self.cooldown[2] and self.direction is None:
            self.randomize_goal(world.w_size)
        if self.direction is not None and self.length > 0:
            vel = pygame.Vector2(1,0).rotate(self.direction).normalize() * self.speed * frame_data.dt
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

    def randomize_goal(self,clamp_size: tuple[int, int]):
        self.direction = random.randint(0, 359)
        self.length = random.randint(self.length_range[0], self.length_range[1])

        eta = pygame.Vector2(50,0).rotate(self.direction).normalize() + self.hitbox.pos
        radius = self.hitbox.radius
        x, y = eta
        if (x < 0 + radius or x > clamp_size[0] - radius or
                y < 0 + radius or y > clamp_size[1] - radius):
            self.direction = random.randint(0, 359)
            self.length = random.randint(50, 90)

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

class FasterSAiEnemy(SimpleAIEnemy):
    def __init__(self, pos: pygame.Vector2,speed_mult = 1.2):
        super().__init__(pos,spd=30,cooldown=0.5,length_range=(130,200))
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

    def update(self, world: "World", frame_data: FrameData):
        self.flash_countdown(frame_data.dt)
        if not self.cooldown[2] and self.direction is None:
            self.roll_randomize_goal(world)
        if self.direction is not None and self.length > 0:
            vel = pygame.Vector2(1, 0).rotate(self.direction).normalize() * self.speed * frame_data.dt
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
        r = random.randint(0,1)
        if r == 1:
            self.randomize_goal(world.w_size)
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
