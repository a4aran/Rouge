import math
import random

import pygame

import gl_var


class Circle:
    def __init__(self,pos: pygame.Vector2,radius):
        self.pos = pos
        self.radius = radius

    def circle_collision(self,circle: "Circle"):
        distance = (self.pos - circle.pos).length()
        return distance <= (self.radius + circle.radius)

    def circle_point_collide(self, point: pygame.Vector2) -> bool:
        dist_sq = (self.pos - point).length_squared()
        return dist_sq <= self.radius * self.radius

    def line_circle_collision(self,p1, p2):
        center = self.pos
        radius = self.radius
        d = p2 - p1
        f = p1 - center

        a = d.dot(d)
        b = 2 * f.dot(d)
        c = f.dot(f) - radius * radius

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return False  # no intersection

        discriminant = math.sqrt(discriminant)
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)

        if (0 <= t1 <= 1) or (0 <= t2 <= 1):
            return True  # intersects segment
        return False

    def intersection_length_with_other(self,other: "Circle"):
        distance = (self.pos - other.pos).length()
        if distance <= (self.radius + other.radius):
            return self.radius + other.radius - distance
        else:
            return 0

    def copy(self):
        return Circle(self.pos.copy(), self.radius)

def angle_to_mouse(pos: pygame.Vector2) -> float:
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    delta = mouse_pos - pos
    # atan2 gives radians, convert to degrees
    angle = math.degrees(math.atan2(delta.y, delta.x))
    return angle


def angle_to_target(main: pygame.math.Vector2, target: pygame.math.Vector2) -> float:
    direction = target - main

    return pygame.Vector2(1,0).angle_to(direction)

def gen_id():
    gl_var.entities_id_counter +=1
    return gl_var.entities_id_counter

def rng_rounding(num: float):
    chance = num - int(num)
    return int(num) + 1 if random.random() < chance else int(num)

class FormulaProvider:
    def __init__(self):
        pass

    @staticmethod
    def damage_upgrade(wave):
        temp = max(2,round(wave*0.425 * FormulaProvider.random_mult() * FormulaProvider._mult_modifier(wave)))
        if wave > 50:
            temp = max(2, round(0.125 * wave * FormulaProvider.random_mult() * FormulaProvider._mult_modifier(wave)))
        return temp

    @staticmethod
    def b_speed_upgrade(wave):
        temp = min(max(20,round(2.2*wave*0.6 * FormulaProvider.random_mult() * FormulaProvider._mult_modifier(wave))),50)
        if wave > 20:
            temp = min(max(30,round(1.9*wave*0.6 * FormulaProvider.random_mult() * FormulaProvider._mult_modifier(wave))),50)
        return temp

    @staticmethod
    def firerate_upgrade(wave):
        temp = max(0.15,round((0.035 * wave*0.5) * FormulaProvider.random_mult() * FormulaProvider._mult_modifier(wave),2))
        if wave > 50:
            temp = max(0.3,round((0.015 * wave*0.5) * FormulaProvider.random_mult() * FormulaProvider._mult_modifier(wave),2))
        elif wave > 30:
            temp = max(0.3,round((0.03 * wave*0.5) * FormulaProvider.random_mult() * FormulaProvider._mult_modifier(wave),2))
        return temp

    @staticmethod
    def boss_hp_mult(wave):
        return max(1, 1 + wave / 6) if wave > 11 else 1

    @staticmethod
    def enemy_scaling(wave):
        scaling = 1
        if 10 <= wave < 20:
            scaling *= 1 + (wave - 5) / 65
        elif 20 <= wave < 30:
            scaling *= 1 + (wave - 15) / 40
        elif 40 > wave >= 30:
            scaling *= 1 + (wave - 10) / 30
        elif 50 > wave >= 40:
            scaling *= 1 + (wave - 5) / 20
        elif 75 > wave >= 50:
            scaling *= wave / 10
        elif 100 > wave >= 75:
            scaling *= wave / 5
        elif wave >= 100:
            scaling *= wave
        return scaling

    @staticmethod
    def enemy_count(wave):
        return wave + 4

    @staticmethod
    def _mult_modifier(wave: int) -> float:
        if wave > 75:
            return 0.7
        elif wave > 50:
            return 0.9
        elif wave > 40:
            return 1.05
        elif wave > 25:
            return 1.2
        else:
            return 1.5

    @staticmethod
    def random_mult():
        return random.randint(90,110) / 100


formulas = FormulaProvider()