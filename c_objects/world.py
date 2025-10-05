import ast
import random

import pygame

import ar_math_helper
import current_game_run_data
import gl_var
from Illusion.frame_data_f import FrameData
from Illusion.go import GlobalObjects
from ar_math_helper import Circle
from c_objects.entities import bosses
from c_objects.entities.enemies import SimpleAIEnemy, FasterSAiEnemy, DoubleSAiEnemy, ShootingEnemy, Enemy, \
    SpawnMarkerEntity
from c_objects.entities.entity import Entity
from c_objects.entities.player import Player
from c_objects.entities.projectiles import Projectile

class World:
    def __init__(self,go: GlobalObjects):
        self.offset = pygame.Vector2(gl_var.window_center[0]-540/2,gl_var.window_center[1]-540/2)
        self.w_size = (540,540)
        self.world_rect = pygame.Rect(self.offset,self.w_size)

        self.player = Player()
        self.entities = []
        self.deleted_entities_amount = 0
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
        self.just_loaded = False

        self.spawn_cycles = 0

        self.textures = {
            "chaos": go.get_custom_object("chaos_boss_sprites"),
            "ice_cube_enemy_sprite": go.get_custom_object("ice_cube_enemy_sprite")
        }

        self.status_effects_textures = {
            "freeze":{
                "16": go.get_custom_object("status_effect_freeze_16")
            },
            "vulnerable": {
                "16": go.get_custom_object("status_effect_vulnerable_16")
            }
        }

    def update(self,fd: FrameData):
        if not self.game_paused:
            self.combined_boss_hp = 0
            for e in self.entities:
                e.update(self,fd)
            self.player.update(self,fd)
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
                        if b.entity_check_collision(p) and b.id not in p.damaged_entities:
                            if not (hasattr(b,"invulnerable") and b.invulnerable):
                                p.damage_entity(b,self)
                    if b.entity_check_collision(self.player):
                        if isinstance(b, bosses.Chaos):
                            if b.try_to_damage_player():
                                self.player.damage(b,5)
                            b.player_damaged()
                    else:
                        if isinstance(b, bosses.Chaos):
                            b.player_damaged_reset()
            self.projectiles = [p for p in self.projectiles if not p.should_delete]
            self.deleted_entities_amount = sum(i.should_delete and i.lifesteal for i in self.entities if isinstance(i,Enemy))
            self.entities = [e for e in self.entities if not e.should_delete]
            self.enemy_projectiles = [ep for ep in self.enemy_projectiles if not ep.should_delete]
            self.boss = [b for b in self.boss if not b.should_delete]

            if self.is_boss_wave:
                if not self.boss:
                    self.wave_on = False
                for b in self.boss:
                    if isinstance(b,Enemy):
                        self.combined_boss_hp += b.health
            elif len(self.entities) <= 0 and self.spawn_cycles == 0:
                self.wave_on = False

            if len(self.entities) <= 3 and self.spawn_cycles > 0:
                self.marker_spawn_cycle()

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
        current_game_run_data.save_manager.write_save_file(self)
        self.wave_count += 1
        self.is_boss_wave = self.wave_count % 10 == 0

        self.combined_boss_max_hp = 0

        if self.is_boss_wave:
            boss_number = ((self.wave_count // 10 - 1) % 2)

            difficultty_mult = ar_math_helper.formulas.difficult_mult(self.wave_count)
            self.boss.append(bosses.boss_list[boss_number](self.w_size,difficultty_mult,self.textures["chaos"]))

            if boss_number == 0:
                self.player.hitbox.pos.xy = (270,270)
            elif boss_number == 1:
                self.player.hitbox.pos.xy = (270,(self.w_size[1]/4) * 3)


            for b in self.boss:
                if isinstance(b, bosses.Boss):
                    self.combined_boss_max_hp += b.max_hp
        else:
            self.spawn_cycles = max(1,int(self.wave_count/10 + 1))
            self.marker_spawn_cycle()
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

    def create_spawn_marker(self, pos: pygame.Vector2):
        classes = ["simple", "faster", "double", "shooter"]
        chances = [100, 0, 0, 0]
        if self.wave_count > 5:
            chances[2] += self.wave_count * 3
        if self.wave_count >= 8:
            chances[1] += 15 * (self.wave_count - 4)
        if self.wave_count >= 15:
            chances[0] = 0
            chances[3] = 30 + (self.wave_count - 15) * 10
        if self.wave_count >= 25:
            chances[1] += 10 * (self.wave_count - 4)
            chances[3] = 30 + (self.wave_count - 15) * 15

        chances = [max(0, c) for c in chances]
        Chosen = random.choices(classes, weights=chances, k=1)[0]

        self.entities.append(SpawnMarkerEntity(pos, Chosen))

    def marker_spawn_cycle(self):
        enemy_count_mult = 1.2 if self.wave_count < 10 else 0.6
        map_center = pygame.Vector2(self.w_size[0] / 2, self.w_size[1] / 2)
        length_range = (150, int(self.w_size[0] / 2 - 20))
        for n in range(ar_math_helper.formulas.enemy_count(int(self.wave_count * enemy_count_mult))):
            vector = pygame.Vector2(random.randint(length_range[0], length_range[1]), 0).rotate(random.randint(0, 359))
            try_pos = vector + map_center
            self.create_spawn_marker(try_pos)
        self.spawn_cycles -= 1
        self.spawn_cycles = max(self.spawn_cycles,0)

    def spawn_enemy(self,pos: pygame.Vector2,type:str):
        classes = {"simple": SimpleAIEnemy,
                   "faster": FasterSAiEnemy,
                   "double": DoubleSAiEnemy,
                   "shooter":ShootingEnemy}
        scaling_hp, scaling_spd = self.get_scaling(type)
        self.entities.append(classes[type](pos, health=scaling_hp, spd=scaling_spd))

    def get_scaling(self,type: str):
        scaling = 35 * ar_math_helper.formulas.enemy_scaling(self.wave_count)
        if type == "simple": return scaling,scaling*0.9
        if type == "faster": return scaling*0.7,scaling*1.05
        if type == "double": return scaling*2,scaling*0.65
        if type == "shooter": return scaling*0.8,scaling*0.8

    def draw(self,surf: pygame.Surface):
        pygame.draw.rect(surf,(0,0,0),self.world_rect,2)
        for p in self.projectiles:
            if isinstance(p,Projectile) and p.layer == "bottom": p.draw(surf,self.offset)
        for e in self.entities:
            if isinstance(e,Enemy):
                if e.texture_name is None:
                    e.draw(surf,self.offset)
                else:
                    e.draw_texture(surf,self.offset,self.textures[e.texture_name + "_enemy_sprite"])
                e.draw_effects(surf,self.status_effects_textures,self.offset)
            else:
                if isinstance(e,Entity): e.draw(surf,self.offset)
        for b in self.boss:
            b.draw(surf,self.offset)
        self.player.draw(surf,self.offset)
        for p in self.projectiles:
            if isinstance(p,Projectile) and p.layer == "top": p.draw(surf,self.offset)
        for ep in self.enemy_projectiles:
            if isinstance(ep,Entity): ep.draw(surf,self.offset)

    def reset(self):
        self.player = Player()
        self.entities = []
        self.boss = []
        self.projectiles = []
        self.enemy_projectiles = []

        self.wave_on = False
        self.wave_count = 0

        self.should_show_vfx = False
        self.vfx_to_show = None
        self.upgrade = [False, 0]
        self.just_loaded = False

        if current_game_run_data.cur_run_data.should_load_save:
            current_game_run_data.cur_run_data.load_save(current_game_run_data.save_manager.loaded_save_file)
            self.player.reset()
            self.load_other(current_game_run_data.save_manager.loaded_save_file)
            if self.wave_count != 0: self.wave_on =True
            current_game_run_data.cur_run_data.should_load_save = False

    def wave_end(self):
        if not self.just_loaded:
            if self.wave_count > 1:
                print(self.wave_count % 5)
                if self.wave_count % 10 == 0:
                    self.upgrade[0] = True
                    self.upgrade[1] = 3
                    print("3")
                elif self.wave_count % 5 == 0:
                    self.upgrade[0] = True
                    self.upgrade[1] = 2
                    print("2")
                elif self.wave_count % 2 == 0:
                    self.upgrade[0] = True
                    self.upgrade[1] = 1
                    print("1")
                else:
                    self.start_wave()
            else:
                self.start_wave()
        else:
            self.just_loaded = False
            self.start_wave()

    def get_closest_enemy(self, pos: pygame.Vector2):
        closest_enemy = None
        closest_dist_sq = float("inf")

        for e in self.entities:
            if isinstance(e,Enemy):
                dist_sq = (e.hitbox.pos - pos).length_squared()
                if dist_sq < closest_dist_sq:
                    closest_dist_sq = dist_sq
                    closest_enemy = e

        return closest_enemy

    def resume_after_upgrade(self):
        self.upgrade = [False, 0]
        self.start_wave()

    def load_other(self,data:str):
        if data is not None:
            data = data["other"]
            self.wave_count = data["wave"]
            self.player.save = data
            self.just_loaded = True