import random

import pygame

from Illusion.frame_data_f import FrameData
from c_objects.entities.entity import Entity


class Enemy(Entity):
    def __init__(self, pos: pygame.Vector2, hitbox_radius: float,health: float,speed: float):
        super().__init__(pos, hitbox_radius)
        self.health = health
        self.speed = speed

    def damage(self,amount: float):
        self.health -= amount
        if self.health <= 0: self.should_delete = True

class SimpleAIEnemy(Enemy):
    def __init__(self, pos: pygame.Vector2):
        super().__init__(pos, 20, 50, 70)
        self.direction = None
        self.cooldown = [0,0.2,False]
        self.length = 0

    def update(self,world: "World",frame_data: FrameData):
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
        self.length = random.randint(50, 130)

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
            self.cooldown[2] = True
        self.hitbox.pos.x = min(max(0 + radius,self.hitbox.pos.x),clamp_size[0] - radius)
        self.hitbox.pos.y = min(max(0 + radius,self.hitbox.pos.y),clamp_size[1] - radius)