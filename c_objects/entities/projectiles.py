import pygame

from Illusion.frame_data_f import FrameData
from c_objects.entities.enemies import Enemy
from c_objects.entities.entity import Entity
from typing import TYPE_CHECKING
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
        if isinstance(entity,Enemy):
            entity.damage(self.damage)
        self.damaged_entities.add(entity.id)

class Bullet(Projectile):
    def __init__(self, pos: pygame.Vector2, direction: float):
        super().__init__(pos, 6, direction, 170,10)
