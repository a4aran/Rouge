import random

import pygame

import gl_var
from Illusion.frame_data_f import FrameData
from ar_math_helper import Circle
from c_objects.entities.enemies import SimpleAIEnemy, FasterSAiEnemy
from c_objects.entities.entity import Entity
from c_objects.entities.player import Player


class World:
    def __init__(self):
        self.offset = pygame.Vector2(180,30)
        self.w_size = (540,540)
        self.world_rect = pygame.Rect(self.offset,self.w_size)

        self.player = Player()
        self.entities = []
        self.projectiles = []

        self.wave_on = False
        self.wave_count = 0

    def update(self,fd: FrameData):
        self.player.update(self,fd)
        for e in self.entities:
            e.update(self,fd)
        for p in self.projectiles:
            if isinstance(p,Entity): p.update(self,fd)

        for e in self.entities:
            if self.player.entity_check_collision(e) and hasattr(e,"damage_on_touch"):
                self.player.damage(e,10)
            for p in self.projectiles:
                if e.entity_check_collision(p) and e.id not in p.damaged_entities:
                    p.damage_entity(e)

        self.projectiles = [p for p in self.projectiles if not p.should_delete]
        self.entities = [e for e in self.entities if not e.should_delete]

        if len(self.entities) <= 0:
            self.wave_on = False

        if not self.wave_on:
            gl_var.entities_id_counter = 0
            self.projectiles = []
            self.entities = []
            self.wave_count += 1
            self.start_wave()

    def start_wave(self):
        temp_circle = Circle((270,270),35)
        for n in range(self.wave_count):
            x = random.randint(13,self.w_size[1] - 13)
            y = random.randint(13,self.w_size[1] - 13)
            try_pos = pygame.Vector2(x,y)
            if temp_circle.circle_point_collide(try_pos):
                ang = (try_pos.angle_to((270,270)) + 180) % 360
                err_vector = pygame.Vector2(50,0).rotate(ang)
                try_pos += err_vector
            self.entities.append(FasterSAiEnemy(try_pos))
        self.player.hitbox.pos.xy = (270,270)
        self.wave_on = True

    def draw(self,surf: pygame.Surface):
        pygame.draw.rect(surf,(0,0,0),self.world_rect,2)
        self.player.draw(surf,self.offset)
        for e in self.entities:
            e.draw(surf,self.offset)
        for p in self.projectiles:
            if isinstance(p,Entity): p.draw(surf,self.offset)

    def reset(self):
        self.player = Player()
        self.entities = []
        self.projectiles = []

        self.wave_on = False
        self.wave_count = 0