import pygame

from Illusion.frame_data_f import FrameData
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from c_objects.world import World
from ar_math_helper import Circle, gen_id


class Entity:
    def __init__(self,pos: pygame.Vector2,hitbox_radius: float):
        self.hitbox = Circle(pos,hitbox_radius)
        self.should_delete = False

        self.id = gen_id()

    def update(self,world: "World",frame_data: FrameData):

        print(self.id)
        self.clamp_pos(world.w_size)

    def draw(self,surf: pygame.Surface,offset: pygame.Vector2):
        offset_pos = self.hitbox.pos + offset
        pygame.draw.circle(surf,(255,255,255),offset_pos,self.hitbox.radius)

    def clamp_pos(self, clamp_size: tuple[int,int]):
        radius = self.hitbox.radius
        self.hitbox.pos.x = min(max(0 + radius,self.hitbox.pos.x),clamp_size[0] - radius)
        self.hitbox.pos.y = min(max(0 + radius,self.hitbox.pos.y),clamp_size[1] - radius)

    def entity_check_collision(self,entity: "Entity"):
        return self.hitbox.circle_collision(entity.hitbox)