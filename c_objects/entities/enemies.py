import copy
import random

import pygame

import ar_math_helper
import gl_var
from Illusion.frame_data_f import FrameData
from Illusion.helper import c_helper
from c_objects.entities import projectiles
from c_objects.entities.entity import Entity
from current_game_run_data import cur_run_data

class SpawnMarkerEntity(Entity):
    def __init__(self, pos: pygame.Vector2,entity_type: str):
        super().__init__(pos, 12)
        self.timer = c_helper.Timer(random.uniform(0.3,1.5))
        self.timer.start()
        self.entity_type = entity_type
        self.rotation = random.randint(0,359)
        self.lifesteal = False

    def update(self,world: "World",frame_data: FrameData):
        self.timer.update(frame_data.dt)
        self.rotation += frame_data.dt * 30
        self.rotation %= 360
        if not self.timer.is_counting_down():
            self.should_delete = True
            world.spawn_enemy(self.hitbox.pos.copy(),self.entity_type)

    def draw(self,surf: pygame.Surface,offset: pygame.Vector2):
        surface = pygame.Surface((self.hitbox.radius*2,self.hitbox.radius*2),pygame.SRCALPHA)
        surface.fill((255,0,0,255*self.timer.get_completion_percentage()))
        surface = pygame.transform.rotate(surface,self.rotation)
        blit_pos = self.hitbox.pos + offset - pygame.Vector2(surface.get_width()/2,surface.get_height()/2)
        surf.blit(surface,blit_pos)

class Enemy(Entity):
    def __init__(self, pos: pygame.Vector2, hitbox_radius: float,health: float,speed: float,dmg: float = 10,texture_name = None):
        super().__init__(pos, hitbox_radius)
        self.health = health
        self.speed = speed
        self.color = (255,255,0)
        self.status_effects = copy.deepcopy(gl_var.status_effect)
        self.immune = set()
        self.atk_dmg = dmg
        self.a_atk_dmg = dmg
        self.texture_name = texture_name
        self.knockback_amount = 0
        self.knockback_dir = 0
        self.lifesteal = True


    def damage(self,world: "World",amount: float,death_info: dict,effects: list = False):
        if self.status_effects["time"]["vulnerable"][2]: amount += self.status_effects["time"]["vulnerable"][3]
        self.health -= amount
        if self.health <= 0:
            self.on_killed(death_info, world)
            return
        if effects:
            for ef in effects:
                if ef[0] == "freeze":
                    self.apply_freeze(ef[1])
                if ef[0] == "vulnerable":
                    self.apply_vulnerable(ef[1],ef[2])
        self.trigger_flash()

    def knockback(self,amount,direction):
        self.knockback_amount = amount
        self.knockback_dir = direction

    def return_knockback(self,dt):
        if self.knockback_amount > 0:
            multiplied_amount = self.knockback_amount * 0.0000001
            amount = multiplied_amount * dt
            capped_amount = min(max(1,amount),3)
            amount = abs(amount-capped_amount)
            amount *= 0.0000001
            amount += capped_amount
            # if self.knockback_amount < 3:
            #     amount += 3
            self.knockback_amount -= amount
            return pygame.Vector2(amount,0).rotate(self.knockback_dir)
        else:
            return None

    def on_killed(self, death_info: dict, world: "World"):
        if death_info is not None:
            if death_info.get("shoot", False) and world.entities:
                # valid targets (exclude self)
                valid_targets = [e for e in world.entities if e.id != self.id]

                if valid_targets:
                    shots = cur_run_data.active_stats[2]["shoot_on_death"][1]

                    # pick unique targets if possible, otherwise allow repeats
                    if shots <= len(valid_targets):
                        chosen_targets = random.sample(valid_targets, shots)
                    else:
                        chosen_targets = [random.choice(valid_targets) for _ in range(shots)]

                    for target in chosen_targets:
                        direction = ar_math_helper.angle_to_target(self.hitbox.pos, target.hitbox.pos)
                        world.projectiles.append(
                            projectiles.AllyProjectile(self.hitbox.pos.copy(), direction, self.id)
                        )

        self.should_delete = True


    def apply_freeze(self,time: float):
        self.status_effects["time"]["freeze"][0] = 0
        self.status_effects["time"]["freeze"][1] = time
        self.status_effects["time"]["freeze"][2] = True

    def apply_vulnerable(self, time: float, strength):
        self.status_effects["time"]["vulnerable"][0] = 0
        self.status_effects["time"]["vulnerable"][1] = time
        self.status_effects["time"]["vulnerable"][2] = True
        self.status_effects["time"]["vulnerable"][3] = ar_math_helper.rng_rounding(strength)

    def update_status_effects(self,fd: FrameData):
        for effect in self.status_effects["time"]:
            data = self.status_effects["time"][effect]
            if data[2]:
                data[0] += fd.dt
                if data[0] >= data[1]:
                    data[0] = 0
                    data[1] = 0
                    data[2] = False
        if not self.status_effects["time"]["vulnerable"][2]: self.status_effects["time"]["vulnerable"][3] = 0

    def get_local_vars(self):
        locs = [self.speed,self.atk_dmg]
        if self.status_effects["time"]["freeze"][2]:
            locs[0] = 0 if "freeze" not in self.immune else self.speed * 0.5
        return locs

    def draw_effects(self,surf:pygame.Surface,effects_textures: dict,offset:pygame.Vector2):
        texture_resolution = None
        if self.hitbox.radius <= 16: texture_resolution = 16
        if texture_resolution is None: return
        pos = self.hitbox.pos - pygame.Vector2(texture_resolution,texture_resolution) + offset

        if self.status_effects["time"]["freeze"][2]:
            surf.blit(effects_textures["freeze"][str(texture_resolution)],pos)
        if self.status_effects["time"]["vulnerable"][2]:
            surf.blit(effects_textures["vulnerable"][str(texture_resolution)],pos)

    def draw_texture(self,surf:pygame.Surface,offset: pygame.Vector2,texture: list[pygame.Surface,pygame.Surface]):
        texture_to_use = texture[1] if self.flash_d[2] else texture[0]
        temp = offset + self.hitbox.pos
        temp -= pygame.Vector2(texture_to_use.get_width()/2,texture_to_use.get_height()/2)
        surf.blit(texture_to_use,temp)

class SimpleAIEnemy(Enemy):
    def __init__(self, pos: pygame.Vector2,health = 50,spd = 50,cooldown = 0.2,length_range: tuple[int,int] = (50,130),texture_name = None):
        super().__init__(pos, 12.5, health, spd,texture_name=texture_name)
        self.direction = None
        self.cooldown = [cooldown * 0.7,cooldown,True]
        self.length = 0
        self.length_range = length_range
        self.damage_on_touch = True
        self.outline_color = (255,0,0)

    def update(self,world: "World",frame_data: FrameData):
        self.check_collision_with_boss(world)
        self.update_status_effects(frame_data)
        loc_speed,self.a_atk_dmg = self.get_local_vars()
        self.flash_countdown(frame_data.dt)
        if not self.cooldown[2] and self.direction is None:
            self.randomize_goal(world.w_size,world.boss,world.player)
        vel = pygame.Vector2(0,0)
        kb = self.return_knockback(frame_data.dt)
        if kb is not None:
            vel = kb
        elif self.direction is not None and self.length > 0:
            vel = pygame.Vector2(1,0).rotate(self.direction).normalize() * loc_speed * frame_data.dt
            self.length -= vel.length()
        self.hitbox.pos += vel
        if self.length <= 0:
            self.direction = None
            self.cooldown[2] = True
        if self.cooldown[2]:
            self.cooldown[0] += frame_data.dt
            if self.cooldown[0] > self.cooldown[1]:
                self.cooldown[0] = 0
                self.cooldown[2] = False
        self.clamp_pos(world.w_size)

    def randomize_goal(self,clamp_size: tuple[int, int],boss,player):
        self.direction = random.randint(0, 359)
        self.length = random.randint(self.length_range[0], self.length_range[1])

        eta = pygame.Vector2(50,0).rotate(self.direction) + self.hitbox.pos
        radius = self.hitbox.radius
        x, y = eta
        if (x < 0 + radius or x > clamp_size[0] - radius or
                y < 0 + radius or y > clamp_size[1] - radius):
            self.direction =  ar_math_helper.angle_to_target(self.hitbox.pos,player.hitbox.pos)

    def check_collision_with_boss(self,world: "World"):
        if world.boss:
            for b in world.boss:
                if self.hitbox.circle_collision(b.hitbox):
                    self.hitbox.pos += (pygame.Vector2(
                        self.hitbox.intersection_length_with_other(b.hitbox),0).
                                        rotate((ar_math_helper.angle_to_target(self.hitbox.pos,b.hitbox.pos) - 180)%360))*1.5
                    self.direction = ar_math_helper.angle_to_target(self.hitbox.pos, world.player.hitbox.pos)
                    self.length = random.randint(self.length_range[0], self.length_range[1])

    def clamp_pos(self, clamp_size: tuple[int, int]):
        radius = self.hitbox.radius
        x, y = self.hitbox.pos

        if (x < 0 + radius or x > clamp_size[0] - radius or
                y < 0 + radius or y > clamp_size[1] - radius):
            self.direction = None
            self.cooldown[0] = self.cooldown[1] * 0.5
            self.cooldown[2] = True
            self.knockback_amount *= 0.5
        self.hitbox.pos.x = min(max(0 + radius,self.hitbox.pos.x),clamp_size[0] - radius)
        self.hitbox.pos.y = min(max(0 + radius,self.hitbox.pos.y),clamp_size[1] - radius)

    def draw(self,surf: pygame.Surface,offset: pygame.Vector2):
        super().draw(surf,offset)
        # if self.direction is not  None:
        #     vec = pygame.Vector2(1,0).rotate(self.direction).normalize() * 100
        #     vec = vec + self.hitbox.pos + offset
        #     pygame.draw.line(surf,(255,0,0),self.hitbox.pos+offset,vec,4)

class FasterSAiEnemy(SimpleAIEnemy):
    def __init__(self, pos: pygame.Vector2,health = 50,spd=30,speed_mult = 1.1):
        super().__init__(pos,health=health,spd=spd,cooldown=0.8,length_range=(130,250),texture_name="ice_cube")
        self.add_speed = self.speed
        self.spd_mult = speed_mult
        self.color = (255,150,0)
        self.immune.add("freeze")

    def update(self,world: "World",frame_data: FrameData):
        self.speed = self.length * self.spd_mult + self.add_speed
        super().update(world,frame_data)

class DoubleSAiEnemy(SimpleAIEnemy):
    def __init__(self, pos: pygame.Vector2,health = 50,spd = 50,cooldown = 0.2,length_range: tuple[int,int] = (50,130)):
        super().__init__(pos,health,spd,cooldown,length_range)
        self.previous_dir = 0
        self.color = (0,0,0)
        self.other_goal_chance = 0.5
        self.atk_dmg = 15

    def update(self, world: "World", frame_data: FrameData):
        self.update_status_effects(frame_data)
        loc_speed, self.a_atk_dmg = self.get_local_vars()
        self.flash_countdown(frame_data.dt)
        if not self.cooldown[2] and self.direction is None:
            self.roll_randomize_goal(world)
        vel = pygame.Vector2(0,0)
        kb = self.return_knockback(frame_data.dt)
        if kb is not None:
            vel = kb * 0.8
        elif self.direction is not None and self.length > 0:
            vel = pygame.Vector2(1,0).rotate(self.direction).normalize() * loc_speed * frame_data.dt
            self.length -= vel.length()
        self.hitbox.pos += vel
        if self.length <= 0:
            self.direction = None
            self.cooldown[2] = True
        if self.cooldown[2]:
            self.cooldown[0] += frame_data.dt
            if self.cooldown[0] > self.cooldown[1]:
                self.cooldown[0] = 0
                self.cooldown[2] = False
        self.clamp_pos(world.w_size)
        if self.direction is not  None:
            self.previous_dir = self.direction

    def roll_randomize_goal(self,world: "World"):
        if random.random() < self.other_goal_chance:
            self.randomize_goal(world.w_size,world.boss,world.player)
        else:
            self.other_goal_randomizer(world)

    def other_goal_randomizer(self,world: "World"):
        loc_dir = self.previous_dir
        if loc_dir is None:
            loc_dir = 0
        loc_dir = (loc_dir + 180) % 360
        self.direction = loc_dir
        self.length = random.randint(self.length_range[0],self.length_range[1])
        eta = pygame.Vector2(50,0).rotate(self.direction).normalize() + self.hitbox.pos
        radius = self.hitbox.radius
        x, y = eta
        clamp_size = world.w_size
        if (x < 0 + radius or x > clamp_size[0] - radius or
                y < 0 + radius or y > clamp_size[1] - radius):
            self.direction = random.randint(0, 359)
            self.length = random.randint(50, 90)

class ShootingEnemy(SimpleAIEnemy):
    def __init__(self, pos: pygame.Vector2,health = 50,spd = 50):
        super().__init__(pos,health=health,spd=spd)
        self.shooting_cooldown = [0,1.25]
        self.color = (0,255,0)
        self.outline_color = (0,0,0)
        self.damage_on_touch = False

    def update(self,world: "World",frame_data: FrameData):
        super().update(world,frame_data)
        self.shooting_cooldown[0] += frame_data.dt
        if self.shooting_cooldown[0] >= self.shooting_cooldown[1]:
            self.shooting_cooldown[0] = 0

            ang = self.hitbox.pos.angle_to(world.player.hitbox.pos) if random.random() < 0.1 else random.randint(0,360)

            world.enemy_projectiles.append(projectiles.EnemyProj(self.hitbox.pos.copy(),ang,100,4))