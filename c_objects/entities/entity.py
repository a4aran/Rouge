import pygame

from Illusion.frame_data_f import FrameData
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from c_objects.world import World
from ar_math_helper import Circle, gen_id


class Entity:
    def __init__(self,pos: pygame.Vector2,hitbox_radius: float,use_flash:bool = False,flash_color: tuple[int,int,int] = (255,255,255)):
        self.hitbox = Circle(pos,hitbox_radius)
        self.should_delete = False

        self.id = gen_id()

        self.color = (255,255,255)
        self.outline_color = (0,0,0)

        self.use_flash = use_flash
        self.flash_color = flash_color
        self.flash_d = [0,0.1,False]

    def update(self,world: "World",frame_data: FrameData):

        self.clamp_pos(world.w_size)

    def draw(self,surf: pygame.Surface,offset: pygame.Vector2):
        offset_pos = self.hitbox.pos + offset
        pygame.draw.circle(surf,self.outline_color,offset_pos,self.hitbox.radius+2)
        col = self.color
        if self.flash_d[2]:
            col = self.flash_color
        pygame.draw.circle(surf,col,offset_pos,self.hitbox.radius)

    def clamp_pos(self, clamp_size: tuple[int,int]):
        radius = self.hitbox.radius
        self.hitbox.pos.x = min(max(0 + radius,self.hitbox.pos.x),clamp_size[0] - radius)
        self.hitbox.pos.y = min(max(0 + radius,self.hitbox.pos.y),clamp_size[1] - radius)

    def entity_check_collision(self,entity: "Entity"):
        return self.hitbox.circle_collision(entity.hitbox)

    def trigger_flash(self):
        self.flash_d[2] = True

    def flash_countdown(self,dt):
        if self.flash_d[2]:
            self.flash_d[0] += dt
            if self.flash_d[0] >= self.flash_d[1]:
                self.flash_d[0] = 0
                self.flash_d[2] = False