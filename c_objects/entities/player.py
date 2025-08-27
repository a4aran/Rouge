import pygame

from Illusion.frame_data_f import FrameData
from ar_math_helper import angle_to_mouse
from c_objects.entities.entity import Entity
from c_objects.entities.projectiles import Bullet
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from c_objects.world import World


class Player(Entity):
    def __init__(self):
        super().__init__(pygame.Vector2(270,270),15)
        self.speed = 120
        self.cooldown = [0,0.5,False]
        self.id = "Player"

    def update(self,world: "World",frame_data: FrameData):
        direction = pygame.Vector2(0, 0)

        if frame_data.keys[pygame.K_w]:
            direction.y -= 1
        if frame_data.keys[pygame.K_s]:
            direction.y += 1
        if frame_data.keys[pygame.K_a]:
            direction.x -= 1
        if frame_data.keys[pygame.K_d]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        velocity = direction * self.speed * frame_data.dt

        self.hitbox.pos += velocity

        self.clamp_pos(world.w_size)

        if self.cooldown[2]:
            self.cooldown[0] += frame_data.dt
            if self.cooldown[0] >= self.cooldown[1]:
                self.cooldown[0] = 0
                self.cooldown[2] = False

        if frame_data.mouse_buttons[0] and not self.cooldown[2]:
            ang = angle_to_mouse(self.hitbox.pos + world.offset)

            world.projectiles.append(Bullet(
            pygame.Vector2(self.hitbox.radius,0)
            .rotate(ang) + self.hitbox.pos,ang))

            self.cooldown[2] = True