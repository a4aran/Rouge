import pygame

def triangle(radius:float,border_width: int,color: tuple[int,int,int],border_color: tuple[int,int,int]):
    surf = pygame.Surface((radius*2,radius*2),pygame.SRCALPHA)
    triangle_points = (
        (radius,0+border_width),
        (0+border_width,radius*2-border_width),
        (radius*2-border_width,radius*2-border_width)
    )
    pygame.draw.polygon(surf,color,triangle_points)
    pygame.draw.polygon(surf,border_color,triangle_points,border_width)
    return surf

def diamond(radius:float,border_width: int,color: tuple[int,int,int],border_color: tuple[int,int,int]):
    points = [
        (radius,border_width),
        (radius*2 -border_width,radius),
        (radius,radius*2 - border_width),
        (border_width,radius)
    ]
    surf = pygame.Surface((radius*2,radius*2),pygame.SRCALPHA)
    pygame.draw.polygon(surf,color,points)
    pygame.draw.polygon(surf,border_color,points,border_width)
    return surf
