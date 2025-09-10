import random

import pygame

import current_game_run_data
import gl_var
from Illusion.frame_data_f import FrameData
from ar_math_helper import Circle
from c_objects.entities import bosses
from c_objects.entities.enemies import SimpleAIEnemy, FasterSAiEnemy, DoubleSAiEnemy, ShootingEnemy, Enemy
from c_objects.entities.entity import Entity
from c_objects.entities.player import Player
from c_objects.entities.projectiles import Projectile

class World:
    def __init__(self):
        self.offset = pygame.Vector2(180,30)
        self.w_size = (540,540)
        self.world_rect = pygame.Rect(self.offset,self.w_size)

        self.player = Player()
        self.entities = []
        self.projectiles = []
        self.enemy_projectiles = []
        self.boss = []

        self.combined_boss_hp = 0
        self.combined_boss_max_hp = 0

        self.wave_on = False
        self.is_boss_wave = False
        self.wave_count = 0

        self.should_show_vfx = False
        self.vfx_to_show = None

        self.game_paused = False
        self.internal_pause = False
        self.pause_timer = [0,0]

        self.upgrade = [False,0]

    def update(self,fd: FrameData):
        if not self.game_paused:
            self.combined_boss_hp = 0
            self.player.update(self,fd)
            for e in self.entities:
                e.update(self,fd)
            for p in self.projectiles:
                if isinstance(p,Entity): p.update(self,fd)
            for ep in self.enemy_projectiles:
                if isinstance(ep,Entity): ep.update(self,fd)
            for b in self.boss:
                if isinstance(b,Entity): b.update(self,fd)

            for e in self.entities:
                if self.player.entity_check_collision(e) and hasattr(e,"damage_on_touch") and e.damage_on_touch:
                    self.player.damage(e,e.a_atk_dmg)
                for p in self.projectiles:
                    if e.entity_check_collision(p) and e.id not in p.damaged_entities and not (hasattr(e,"no_projectile_collision") and e.no_projectile_collision):
                        if isinstance(p,Projectile):
                            p.damage_entity(e,self)
            for ep in self.enemy_projectiles:
                if self.player.entity_check_collision(ep):
                    ep.damage_entity(self.player,self)
            if self.boss:
                for b in self.boss:
                    for p in self.projectiles:
                        if b.entity_check_collision(p) and b.id:
                            p.damage_entity(b,self)

            self.projectiles = [p for p in self.projectiles if not p.should_delete]
            self.entities = [e for e in self.entities if not e.should_delete]
            self.enemy_projectiles = [ep for ep in self.enemy_projectiles if not ep.should_delete]
            self.boss = [b for b in self.boss if not b.should_delete]

            if self.is_boss_wave:
                if not self.boss:
                    self.wave_on = False
                for b in self.boss:
                    if isinstance(b,Enemy):
                        self.combined_boss_hp += b.health
            elif len(self.entities) <= 0:
                self.wave_on = False

            if not self.wave_on:
                gl_var.entities_id_counter = 0
                self.projectiles = []
                self.enemy_projectiles = []
                self.entities = []
                self.wave_end()

        if self.game_paused:
            if self.internal_pause:
                self.pause_timer[0] += fd.dt
                if self.pause_timer[0] > self.pause_timer[1]:
                    self.unpause_internally()
                    if self.should_show_vfx:
                        self.should_show_vfx = False
                        self.vfx_to_show = None

    def start_wave(self):
        self.wave_count += 1
        self.is_boss_wave = self.wave_count % 10 == 0

        self.combined_boss_max_hp = 0

        if self.is_boss_wave:
            boss_number = ((self.wave_count // 10 - 1) % 5)

            hp_mult = min(1,1 + self.wave_count/2.5) if self.wave_count > 11 else 1
            self.boss.append(bosses.boss_list[0](self.w_size,hp_mult))

            for b in self.boss:
                if isinstance(b, Enemy):
                    self.combined_boss_max_hp += b.health
        else:
            map_center = pygame.Vector2(self.w_size[0]/2,self.w_size[1]/2)
            length_range = (150,int(self.w_size[0]/2 - 20))
            for n in range(self.wave_count + 4):
                vector = pygame.Vector2(random.randint(length_range[0],length_range[1]),0).rotate(random.randint(0,359))
                try_pos = vector + map_center
                self.spawn_enemy(try_pos)
        self.player.hitbox.pos.xy = (270,270)
        self.player.reset_cooldowns()
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

    def spawn_enemy(self,pos: pygame.Vector2,type:str = None):
        classes = {"simple": SimpleAIEnemy,
                   "faster": FasterSAiEnemy,
                   "double": DoubleSAiEnemy,
                   "shooter":ShootingEnemy}
        if type is None:
            chances = [100,0,0,0]
            if 5 < self.wave_count:
                chances[2] += self.wave_count * 3
            if self.wave_count >= 8:
                chances[1] += 15 * (self.wave_count - 4)
            if self.wave_count >= 15:
                # chances[2] += min(20 * (self.wave_count - 14),70)
                chances[0] = 0
                chances[3] = 30 + (self.wave_count - 15) * 10
            if self.wave_count >= 25:
                chances[1] += 10 * (self.wave_count - 4)
                chances[3] = 30 + (self.wave_count - 15) * 15

            Chosen = random.choices(list(classes.keys()),weights=chances,k=1)[0]
            scaling_hp,scaling_spd = self.get_scaling(Chosen)
            self.entities.append(classes[Chosen](pos,health=scaling_hp,spd=scaling_spd))
        else:
            scaling_hp, scaling_spd = self.get_scaling(type)
            self.entities.append(classes[type](pos, health=scaling_hp, spd=scaling_spd))

    def get_scaling(self,type: str):
        scaling = 35
        if 10 < self.wave_count < 20:
            scaling *= 1 + (self.wave_count - 5) / 65
        elif 20 < self.wave_count < 30:
            scaling *= 1 + (self.wave_count-5) / 35
        elif self.wave_count > 30:
            scaling *= 1 + (self.wave_count-5) / 25
        if type == "simple": return scaling,scaling*0.9
        if type == "faster": return scaling*0.7,scaling*1.05
        if type == "double": return scaling*2,scaling*0.65
        if type == "shooter": return scaling*0.8,scaling*0.8

    def draw(self,surf: pygame.Surface):
        pygame.draw.rect(surf,(0,0,0),self.world_rect,2)
        for e in self.entities:
            e.draw(surf,self.offset)
        for b in self.boss:
            b.draw(surf,self.offset)
        self.player.draw(surf,self.offset)
        for p in self.projectiles:
            if isinstance(p,Entity): p.draw(surf,self.offset)
        for ep in self.enemy_projectiles:
            if isinstance(ep,Entity): ep.draw(surf,self.offset)

    def reset(self):
        self.player = Player()
        self.entities = []
        self.projectiles = []
        self.enemy_projectiles = []

        self.wave_on = False
        self.wave_count = 0

        self.should_show_vfx = False
        self.vfx_to_show = None
        self.upgrade = [False, 0]

        current_game_run_data.cur_run_data.reset()
        self.player.reset()

    def wave_end(self):
        if self.wave_count > 1:
            if self.wave_count % 10 == 0:
                self.upgrade[0] = True
                self.upgrade[1] = 3
            elif self.wave_count % 2 == 0:
                self.upgrade[0] = True
                self.upgrade[1] = 1
            elif self.wave_count % 5 == 0:
                self.upgrade[0] = True
                self.upgrade[1] = 2
            else:
                self.start_wave()
        else:
            self.start_wave()

    def resume_after_upgrade(self):
        self.upgrade = [False, 0]
        self.start_wave()
