import math

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

def angle_to_mouse(pos: pygame.Vector2) -> float:
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    delta = mouse_pos - pos
    # atan2 gives radians, convert to degrees
    angle = math.degrees(math.atan2(delta.y, delta.x))
    return angle

def gen_id():
    gl_var.entities_id_counter +=1
    return gl_var.entities_id_counter

class FormulaProvider:
    def __init__(self):
        pass

    @staticmethod
    def damage_upgrade(wave,random):
        mult = 1.1
        if wave > 10:
            mult =0.9
            if wave > 15:
                mult = 0.7
        return max(2,round(1*wave*0.8 * random * mult))

    @staticmethod
    def b_speed_upgrade(wave,random):
        return max(20,round(3*wave*0.7 * random))

    @staticmethod
    def firerate_upgrade(wave,random):
        return max(0.15,round((0.02 * wave*0.5) * random,2))

formulas = FormulaProvider()