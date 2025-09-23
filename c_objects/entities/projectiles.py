import random

import pygame

import ar_math_helper
import drawer
from Illusion.frame_data_f import FrameData
from c_objects.entities.entity import Entity
from typing import TYPE_CHECKING

from current_game_run_data import cur_run_data

if TYPE_CHECKING:
    from c_objects.world import World

class Projectile(Entity):
    def __init__(self, pos: pygame.Vector2,radius:float,direction: float,speed:float,damage: float,on_death:dict):
        super().__init__(pos, radius)
        self.speed = speed
        self.direction = direction
        self.damaged_entities = set()
        self.damage = damage
        self.color = (255,0,0)
        self.effects = []
        self.on_death = on_death

    def update(self,world: "World",frame_data: FrameData):
        vel = pygame.Vector2(1,0).rotate(self.direction).normalize()
        self.hitbox.pos += vel * self.speed * frame_data.dt
        self.clamp_pos(world.w_size)

    def clamp_pos(self, clamp_size: tuple[int, int]):
        radius = self.hitbox.radius
        x, y = self.hitbox.pos

        if (x < 0 + radius or x > clamp_size[0] - radius or
                y < 0 + radius or y > clamp_size[1] - radius):
            self.should_delete = True

    def damage_entity(self, entity: Entity,world: "World"):
        from c_objects.entities.enemies import Enemy
        if isinstance(entity,Enemy):
            entity.damage(world,self.damage,self.on_death,self.effects)
        self.damaged_entities.add(entity.id)

    def draw(self,surf: pygame.Surface,offset: pygame.Vector2):
        offset_pos = self.hitbox.pos + offset
        temp_s = drawer.diamond(self.hitbox.radius+2,2,self.color,self.outline_color)
        # pygame.draw.circle(surf,(255,255,255,100),offset_pos,self.hitbox.radius)
        surf.blit(temp_s,(offset_pos[0]-temp_s.get_width()/2,offset_pos[1]-temp_s.get_height()/2))

class PierceProj(Projectile):
    def __init__(self, pos: pygame.Vector2, direction: float,dmg: float,spd: float,pierce: int,bounce_chance: float,on_death: dict):
        super().__init__(pos, 6, direction, spd,dmg,on_death)
        self.pierce = pierce
        self.bounce_chance = bounce_chance
        self.outline_color = (255,255,255)
        self.color = (255,255,255)

    def update(self,world: "World",frame_data: FrameData):
        super().update(world,frame_data)
        if self.pierce < 1: self.should_delete = True

    def damage_entity(self, entity: Entity,world: "World"):
        super().damage_entity(entity,world)
        if hasattr(entity,"no_pierce") and entity.no_pierce:
            self.pierce = 0
        else:
            self.pierce -= 1

    def clamp_pos(self, clamp_size: tuple[int, int]):
        radius = self.hitbox.radius
        x, y = self.hitbox.pos

        bounced = False
        vel = pygame.Vector2(1, 0).rotate(self.direction)

        # Left or right walls
        if cur_run_data.get_random_chance(self.bounce_chance):
            if x < radius or x > clamp_size[0] - radius:
                self.direction = 180 - self.direction

            # Vertical walls (top/bottom)
            if y < radius or y > clamp_size[1] - radius:
                self.direction = -self.direction

            if bounced:
                self.damaged_entities = set()
                # Recompute direction from reflected velocity
                self.direction = vel.angle_to(pygame.Vector2(1, 0))
                # Clamp position inside the bounds so it doesn't get stuck
                self.hitbox.pos.x = max(radius, min(x, clamp_size[0] - radius))
                self.hitbox.pos.y = max(radius, min(y, clamp_size[1] - radius))
        else:
            if (x < 0 + radius or x > clamp_size[0] - radius or
                    y < 0 + radius or y > clamp_size[1] - radius):
                self.should_delete = True

class AllyProjectile(PierceProj):
    def __init__(self, pos: pygame.Vector2, direction: float,shooter_id):
        super().__init__(pos, direction, 8, 150, 1, 0, None)
        self.damaged_entities.add(shooter_id)
        self.color = (255,255,100)
        self.outline_color = (255,255,100)

class FreezePP(PierceProj):
    def __init__(self, pos: pygame.Vector2, direction: float,dmg: float,spd: float,pierce: int,bounce_chance: float,on_death: dict):
       super().__init__(pos,direction,dmg,spd,pierce,bounce_chance,on_death)
       self.effects = [["freeze", 0.5]]
       self.color = (0,255,255)
       self.outline_color = (0,255,255)

class HomingPP(PierceProj):
    def __init__(self, pos: pygame.Vector2, direction: float, dmg: float, spd: float, pierce: int, bounce_chance: float,
                 on_death: dict):
        super().__init__(pos, direction, dmg, spd, pierce, bounce_chance, on_death)
        self.target = None
        self.step = spd * 0.8
        self.color = (0,155,0)
        self.outline_color = (0,155,0)

    def update(self,world: "World",frame_data: FrameData):
        if world.entities:
            if self.target != "i":
                if self.target is not None and (self.target.id in self.damaged_entities or self.target not in world.entities): self.target = None
            if self.target is None:
                ce = world.get_closest_enemy(self.hitbox.pos)
                if ce is not None and not ce.id in self.damaged_entities:
                    self.target = ce
                else:
                    valid_targets = [e for e in world.entities if e.id not in self.damaged_entities]
                    if valid_targets:
                        self.target = random.choice(valid_targets)
                    else:
                        self.target = "i"
            if self.target != "i":
                target_angle = ar_math_helper.angle_to_target(self.hitbox.pos,self.target.hitbox.pos)
                diff = (target_angle - self.direction + 180) % 360 - 180
                step = self.step * frame_data.dt
                if abs(diff) <= step:
                    self.direction = target_angle
                else:
                    self.direction = (self.direction + step * (1 if diff > 0 else -1)) % 360
        super().update(world,frame_data)

class EnemyProj(Projectile):
    def __init__(self, pos: pygame.Vector2, direction: float, speed: float, damage: float):
        super().__init__(pos, 4, direction, speed, damage,None)
        self.color = (0,0,0)
        self.outline_color = (255,0,0)
        self.color = (255,0,0)

    def damage_entity(self, entity: Entity,world: "World"):
        if getattr(entity,"id",None) == "Player":
            entity.damage(self,self.damage)
        self.should_delete = True