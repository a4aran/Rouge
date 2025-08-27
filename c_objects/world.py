import pygame

import gl_var
from Illusion.frame_data_f import FrameData
from c_objects.entities.enemies import SimpleAIEnemy
from c_objects.entities.entity import Entity
from c_objects.entities.player import Player


class World:
    def __init__(self):
        self.offset = pygame.Vector2(180,30)
        self.w_size = (540,540)
        self.world_rect = pygame.Rect(self.offset,self.w_size)

        self.player = Player()
        self.entities = [SimpleAIEnemy((100,100))]
        self.projectiles = []

        self.wave_on = True

    def update(self,fd: FrameData):
        self.player.update(self,fd)
        for e in self.entities:
            e.update(self,fd)
        for p in self.projectiles:
            if isinstance(p,Entity): p.update(self,fd)

        for e in self.entities:
            self.player.entity_check_collision(e)
            for p in self.projectiles:
                if e.entity_check_collision(p) and e.id not in p.damaged_entities:
                    p.damage_entity(e)
            print(e.health)

        self.projectiles = [p for p in self.projectiles if not p.should_delete]
        self.entities = [e for e in self.entities if not e.should_delete]

        if len(self.entities) <= 0:
            self.wave_on = False

        if not self.wave_on:
            gl_var.entities_id_counter = 0
            self.projectiles = []
            self.entities = []

    def draw(self,surf: pygame.Surface):
        pygame.draw.rect(surf,(0,0,0),self.world_rect,2)
        self.player.draw(surf,self.offset)
        for e in self.entities:
            e.draw(surf,self.offset)
        for p in self.projectiles:
            if isinstance(p,Entity): p.draw(surf,self.offset)