import math
import random

import pygame

import ar_math_helper
import gl_var
from Illusion.frame_data_f import FrameData
from c_objects.entities.enemies import Enemy, SimpleAIEnemy
from c_objects.entities.entity import Entity
from c_objects.entities.projectiles import EnemyProj
import ar_math_helper as ar_math

# - Crowd Master Boss - #
class CrowdMaster(Enemy):
    def __init__(self, w_size,hp_mult):
        super().__init__(pygame.Vector2(w_size[0]/2,0), 120, 1500 * hp_mult, 0)
        self.w_size = w_size
        self.no_pierce = True
        self.minion_spawn_cooldown = [2,3]
        self.shooting_cooldown = [0.5,2]
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
            world.entities.append(SpawnProjectile(loc_pos,random_dir,random_distance,["simple","faster"],[0.67,0.33]))

    def shoot(self,world):
        ang = random.randint(30, 150) if random.random() > 0.2 else self.ang_to_p
        pos = self.hitbox.pos + pygame.Vector2(self.hitbox.radius, 0).rotate(ang)
        world.enemy_projectiles.append(EnemyProj(pos,ang,100,4))
        self.shooting[2] += 1

    def clamp_pos(self, clamp_size: tuple[int,int]):
        return

# ^ Spawning Projectile ^ #
class SpawnProjectile(Entity):
    def __init__(self, pos: pygame.Vector2,angle: int,distance: int,enemies_to_spawn_list: list,spawn_chances:list,speed:int = 40):
        super().__init__(pos, 7)
        self.angle = angle
        self.dist = distance
        self.speed = speed
        self.no_projectile_collision = True
        self.enemies = enemies_to_spawn_list
        self.chances = spawn_chances

    def update(self,world: "World",frame_data: FrameData):
        vel = pygame.Vector2(1,0).rotate(self.angle) * self.speed * frame_data.dt
        self.dist -= vel.length()
        self.force_spawn(world.w_size)
        if self.dist < 0:
            self.should_delete = True
            enemy_type = random.choices(self.enemies, weights=self.chances, k=1)[0]
            world.spawn_enemy(self.hitbox.pos, enemy_type)
        self.hitbox.pos += vel

    def draw(self,surf: pygame.Surface,offset: pygame.Vector2):
        double_radius = self.hitbox.radius * 2
        temp = pygame.Surface((double_radius,double_radius),pygame.SRCALPHA)
        temp.fill((255,255,255))
        pygame.draw.rect(temp,(0,0,0),(0,0,double_radius,double_radius),2)
        temp = pygame.transform.rotate(temp,-self.angle)
        surf.blit(temp,(offset.x + self.hitbox.pos.x - temp.get_width()/2,offset.y + self.hitbox.pos.y - temp.get_height()/2))

    def force_spawn(self,w_size):
        if 0 < self.hitbox.pos.x or self.hitbox.pos.x > w_size[0]\
            or 0 < self.hitbox.pos.y or self.hitbox.pos.y > w_size[1]:
            self.dist = -1

# - Chaos Boss - #
class Chaos(Enemy):
    def __init__(self, w_size,hp_mult):
        super().__init__(pygame.Vector2(w_size[0]/2,w_size[1]/4), 60, 1111 * hp_mult, 220)
        self.max_hp = self.health
        self.w_size = w_size
        self.ang_to_p = 0
        self.get_new_direction = True
        self.direction = 0
        self.wave_start_cooldown = 0.1
        self.touch_dmg_cooldown = [0,0.5,True]
        self.can_touch_damage= True
        self.color = (100,100,130)
        self.invulnerable = False
        self.shoot_cooldown = [0,0.3]
        self.phase = self.get_phase()

    def update(self,world: "World",frame_data: FrameData):
        self.flash_countdown(frame_data.dt)
        self.phase = self.get_phase()
        self.shoot_cooldown[1] = 0.25 if self.phase == 1 else 0.15
        if not self.touch_dmg_cooldown[2]:
            self.touch_dmg_cooldown[0] += frame_data.dt
            if self.touch_dmg_cooldown[0] > self.touch_dmg_cooldown[1]:
                self.touch_dmg_cooldown[2] = True
        if self.wave_start_cooldown > 0:
            self.wave_start_cooldown -= frame_data.dt
        else:
            if self.get_new_direction:
                self.ang_to_p = ar_math_helper.angle_to_target(self.hitbox.pos,world.player.hitbox.pos)
                if self.try_to_damage_player():
                    temp_dir =(self.ang_to_p + random.randint(-50,50)) % 360
                    self.direction = temp_dir if abs(temp_dir - self.direction) > 20 else (temp_dir - 180)%360
                else:
                    self.direction = (self.ang_to_p -180)%360
                self.get_new_direction = False
            add_speed = 0 if self.try_to_damage_player() else 100
            self.hitbox.pos = self.hitbox.pos + (pygame.Vector2(1,0).rotate(self.direction).normalize() * (self.speed + add_speed) * frame_data.dt)
            self.shoot_cooldown[0] += frame_data.dt
            if self.shoot_cooldown[0] > self.shoot_cooldown[1]:
                self.shoot_cooldown[0] = 0
                self.shoot(world)
                if not self.try_to_damage_player():
                    self.shoot(world)

        print(self.get_new_direction)
        self.clamp_pos(world.w_size)
        self.outline_color = (255,0,0) if self.try_to_damage_player() else (0,0,0)
        self.set_invulnerable()

    def clamp_pos(self, clamp_size: tuple[int,int]):
        radius = self.hitbox.radius
        if 0 + radius > self.hitbox.pos.x or self.hitbox.pos.x > self.w_size[0] - radius\
            or 0 + radius > self.hitbox.pos.y or self.hitbox.pos.y > self.w_size[1] - radius:
            self.get_new_direction = True
        self.hitbox.pos.x = min(max(0 + radius,self.hitbox.pos.x),clamp_size[0] - radius)
        self.hitbox.pos.y = min(max(0 + radius,self.hitbox.pos.y),clamp_size[1] - radius)

    def try_to_damage_player(self):
        return self.can_touch_damage and self.touch_dmg_cooldown[2]

    def player_damaged(self):
        self.can_touch_damage = False
        self.touch_dmg_cooldown[0] = 0
        self.touch_dmg_cooldown[2] = False

    def player_damaged_reset(self):
        self.can_touch_damage = True

    def set_invulnerable(self):
        self.invulnerable = not self.try_to_damage_player()

    def shoot(self,world):
        ang = (self.direction - 180 + random.randint(-10 * self.phase,10 * self.phase))%360 if random.random() < 0.7 else (ar_math.angle_to_target(self.hitbox.pos,world.player.hitbox.pos) + random.randint(-30,30))%360
        pos = self.hitbox.pos + pygame.Vector2(self.hitbox.radius, 0).rotate(ang)
        if self.phase == 1:
            world.enemy_projectiles.append(EnemyProj(pos,ang,200,2))
        else:
            if random.random() < 0.3:
                world.entities.append(SpawnProjectile(pos,ang,random.randint(150,200),["faster"],[1],200))
            else:
                world.enemy_projectiles.append(EnemyProj(pos,ang,200,2))

    def get_phase(self):
        if self.health != 0 and (self.health / self.max_hp) < 0.3:
            return 2
        else:
            return 1


boss_list = [CrowdMaster, Chaos]