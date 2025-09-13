import math
import random

import pygame

import gl_var
from Illusion.frame_data_f import FrameData
from c_objects.entities.enemies import Enemy, SimpleAIEnemy
from c_objects.entities.entity import Entity
from c_objects.entities.projectiles import EnemyProj
import ar_math_helper as ar_math


class CrowdMaster(Enemy):
    def __init__(self, w_size,hp_mult):
        super().__init__(pygame.Vector2(w_size[0]/2,0), 120, 1000 * hp_mult, 0)
        self.w_size = w_size
        self.no_pierce = True
        self.minion_spawn_cooldown = [2,2.5]
        self.shooting_cooldown = [0.5,1.5]
        self.shooting = [0,0.1,0,6,False]
        self.ang_to_p = 0

    def draw(self, surf: pygame.Surface, offset: pygame.Vector2):
        temp = pygame.Surface(self.w_size, pygame.SRCALPHA)
        pygame.draw.circle(temp, self.outline_color, self.hitbox.pos, self.hitbox.radius + 3)
        pygame.draw.circle(temp, self.color, self.hitbox.pos, self.hitbox.radius)
        surf.blit(temp, offset)

    def update(self,world: "World",frame_data: FrameData):
        super().update(world,frame_data)
        self.ang_to_p = ar_math.angle_to_target(self.hitbox.pos, world.player.hitbox.pos)
        print(self.ang_to_p)

        if self.shooting[4]:
            self.shooting[0] += frame_data.dt
            if self.shooting[0] >= self.shooting[1]:
                self.shooting[0] = 0
                self.shoot(world)
                if self.shooting[2] >= self.shooting[3]:
                    self.shooting[4] = False
                    self.shooting[2] = 0
        else:
            self.shooting_cooldown[0] += frame_data.dt
            if self.shooting_cooldown[0] >= self.shooting_cooldown[1]:
                self.shooting_cooldown[0] = 0
                self.shooting[4] = True

        self.minion_spawn_cooldown[0] += frame_data.dt
        if self.minion_spawn_cooldown[0] >= self.minion_spawn_cooldown[1]:
            self.minion_spawn_cooldown[0] = 0
            if len(world.entities) < 15:
                self.spawn_minions(world,4)
            else:
                self.spawn_minions(world,1)

    def spawn_minions(self,world: "World",amount):
        for i in range(amount):
            random_dir = random.randint(30,150)
            random_distance = random.randint(40,100)
            loc_pos = self.hitbox.pos + pygame.Vector2(self.hitbox.radius,0).rotate(random_dir)
            world.entities.append(SpawnProjectile(loc_pos,random_dir,random_distance))

    def shoot(self,world):
        ang = random.randint(30, 150) if random.random() > 0.2 else self.ang_to_p
        pos = self.hitbox.pos + pygame.Vector2(self.hitbox.radius, 0).rotate(ang)
        world.enemy_projectiles.append(EnemyProj(pos,ang,100,4))
        self.shooting[2] += 1

    def clamp_pos(self, clamp_size: tuple[int,int]):
        return

class SpawnProjectile(Entity):
    def __init__(self, pos: pygame.Vector2,angle: int,distance: int):
        super().__init__(pos, 7)
        self.angle = angle
        self.dist = distance
        self.speed = 40
        self.no_projectile_collision = True

    def update(self,world: "World",frame_data: FrameData):
        vel = pygame.Vector2(1,0).rotate(self.angle) * self.speed * frame_data.dt
        self.dist -= vel.length()
        if self.dist < 0:
            self.should_delete = True
            world.spawn_enemy(self.hitbox.pos,"faster" if random.random() < 0.33 else "simple")
        self.hitbox.pos += vel

    def draw(self,surf: pygame.Surface,offset: pygame.Vector2):
        double_radius = self.hitbox.radius * 2
        temp = pygame.Surface((double_radius,double_radius),pygame.SRCALPHA)
        temp.fill((255,255,255))
        pygame.draw.rect(temp,(0,0,0),(0,0,double_radius,double_radius),2)
        temp = pygame.transform.rotate(temp,-self.angle)
        surf.blit(temp,(offset.x + self.hitbox.pos.x - temp.get_width()/2,offset.y + self.hitbox.pos.y - temp.get_height()/2))

boss_list = [CrowdMaster]