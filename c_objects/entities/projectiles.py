import pygame

from Illusion.frame_data_f import FrameData
from c_objects.entities.entity import Entity
from typing import TYPE_CHECKING

from current_game_run_data import cur_run_data

if TYPE_CHECKING:
    from c_objects.world import World

class Projectile(Entity):
    def __init__(self, pos: pygame.Vector2,radius:float,direction: float,speed:float,damage: float):
        super().__init__(pos, radius)
        self.speed = speed
        self.direction = direction
        self.damaged_entities = set()
        self.damage = damage
        self.color = (255,0,0)
        self.effects = []

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

    def damage_entity(self, entity: Entity):
        from c_objects.entities.enemies import Enemy
        if isinstance(entity,Enemy):
            entity.damage(self.damage,self.effects)
        self.damaged_entities.add(entity.id)

class PierceProj(Projectile):
    def __init__(self, pos: pygame.Vector2, direction: float,dmg: float,spd: float,pierce: int,bounce_chance: float):
        super().__init__(pos, 6, direction, spd,dmg)
        self.pierce = pierce
        self.bounce_chance = bounce_chance

    def update(self,world: "World",frame_data: FrameData):
        super().update(world,frame_data)
        if self.pierce < 1: self.should_delete = True

    def damage_entity(self, entity: Entity):
        super().damage_entity(entity)
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
            print(vel)
            if x < radius or x > clamp_size[0] - radius:
                self.direction = 180 - self.direction

            # Vertical walls (top/bottom)
            if y < radius or y > clamp_size[1] - radius:
                self.direction = -self.direction
            print(vel)

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

class FreezePP(PierceProj):
    def __init__(self, pos: pygame.Vector2, direction: float,dmg: float,spd: float,pierce: int,bounce_chance: float):
       super().__init__(pos,direction,dmg,spd,pierce,bounce_chance)
       self.effects = [["freeze", 0.5]]
       self.color = (0,255,255)

class EnemyProj(Projectile):
    def __init__(self, pos: pygame.Vector2, direction: float, speed: float, damage: float):
        super().__init__(pos, 4, direction, speed, damage)
        self.color = (0,0,0)
        self.outline_color = (255,0,0)

    def damage_entity(self, entity: Entity):
        if getattr(entity,"id",None) == "Player":
            entity.damage(self,self.damage)
        self.should_delete = True