import random

import pygame

import gl_var
from Illusion.frame_data_f import FrameData
from ar_math_helper import Circle
from c_objects.entities.enemies import SimpleAIEnemy, FasterSAiEnemy, DoubleSAiEnemy
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

        self.should_show_vfx = False
        self.vfx_to_show = None

        self.game_paused = False
        self.internal_pause = False
        self.pause_timer = [0,0]

    def update(self,fd: FrameData):
        if not self.game_paused:
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

        if self.game_paused:
            if self.internal_pause:
                self.pause_timer[0] += fd.dt
                if self.pause_timer[0] > self.pause_timer[1]:
                    self.unpause_internally()
                    if self.should_show_vfx:
                        self.should_show_vfx = False
                        self.vfx_to_show = None

    def start_wave(self):
        # temp_circle = Circle((270,270),35)
        # for n in range(self.wave_count):
        #     x = random.randint(13,self.w_size[1] - 13)
        #     y = random.randint(13,self.w_size[1] - 13)
        #     try_pos = pygame.Vector2(x,y)
        #     if temp_circle.circle_point_collide(try_pos):
        #         ang = (try_pos.angle_to((270,270)) + 180) % 360
        #         err_vector = pygame.Vector2(50,0).rotate(ang)
        #         try_pos += err_vector
        #     self.entities.append(FasterSAiEnemy(try_pos))
        # self.player.hitbox.pos.xy = (270,270)
        # self.wave_on = True
        map_center = pygame.Vector2(self.w_size[0]/2,self.w_size[1]/2)
        length_range = (100,int(self.w_size[0]/2 - 20))
        for n in range(self.wave_count + 4):
            vector = pygame.Vector2(random.randint(length_range[0],length_range[1]),0).rotate(random.randint(0,359))
            try_pos = vector + map_center
            self.spawn_enemy(try_pos)
        self.player.hitbox.pos.xy = (270,270)
        self.wave_on = True

        self.should_show_vfx = True
        self.vfx_to_show = "wave_start"
        self.pause_internally(1)

    def pause_internally(self,timer_amount):
        self.game_paused = True
        self.internal_pause = True
        self.pause_timer[1] = timer_amount

    def unpause_internally(self):
        self.game_paused = False
        self.internal_pause = False
        self.pause_timer[0] = 0
        self.pause_timer[0] = 0

    def spawn_enemy(self,pos: pygame.Vector2):
        classes = [SimpleAIEnemy,FasterSAiEnemy,DoubleSAiEnemy]
        chances = [100,0,20]
        if self.wave_count >= 5:
            chances[1] += 20 * (self.wave_count - 4)
        if self.wave_count >= 15:
            # chances[2] += min(20 * (self.wave_count - 14),70)
            chances[0] = 0
            chances[2] = 80

        Chosen = random.choices(classes,weights=chances,k=1)[0]
        self.entities.append(Chosen(pos))

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

        self.should_show_vfx = False
        self.vfx_to_show = None