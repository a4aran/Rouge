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

def angle_to_mouse(pos: pygame.Vector2) -> float:
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    delta = mouse_pos - pos
    # atan2 gives radians, convert to degrees
    angle = math.degrees(math.atan2(delta.y, delta.x))
    return angle

def gen_id():
    gl_var.entities_id_counter +=1
    return gl_var.entities_id_counter