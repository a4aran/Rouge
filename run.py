import pygame

import app_data
import engine_settings

pygame.init()
hws = True
try:
    pygame.mixer.init()
except:
    hws = False
    print("No audio hardware found.")
import window_size
from game import Game

from Illusion.frame_data_f import FrameData as Fd

temp = app_data.window_title
if app_data.window_title is None:
    temp = "Illu Engine Window"
pygame.display.set_caption(temp)

if app_data.icon_img_path is not None:
    try:
        icon = pygame.image.load(app_data.icon_img_path)
    except:
        icon = pygame.image.load("." + app_data.icon_img_path)

window = pygame.display.set_mode((window_size.width,window_size.height))
game_o = Game(hws)

cursor_img = [None,None]

if app_data.custom_cursor["default"] is not None:
    try:
        cursor_img[0] = pygame.image.load(app_data.custom_cursor["default"])
    except:
        cursor_img[0] = pygame.image.load("." + app_data.custom_cursor["default"])
    cursor_img[0] = pygame.cursors.Cursor((0,0),cursor_img[0])
if app_data.custom_cursor["hover"] is not None:
    try:
        cursor_img[1] = pygame.image.load(app_data.custom_cursor["hover"])
    except:
        cursor_img[1] = pygame.image.load("." + app_data.custom_cursor["hover"])
    cursor_img[1] = pygame.cursors.Cursor((0,0),cursor_img[1])


clock = pygame.time.Clock()
game_on = True
frame_data = Fd()
while game_on:
    frame_data.dt = clock.tick(engine_settings.desired_fps) / 1000
    frame_data.dt = min(frame_data.dt,engine_settings.max_delta_time)
    frame_data.reset_mbtn()
    frame_data.hovers = False
    frame_data.keys = pygame.key.get_pressed()

    if engine_settings.show_debug_info:
        if engine_settings.print_fps: print(clock.get_fps())

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            game_on = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                frame_data.mbtn_just_pressed[0] = True
            elif e.button == 2:
                frame_data.mbtn_just_pressed[1] = True
            elif e.button == 3:
                frame_data.mbtn_just_pressed[2] = True

    window.fill((255,255,255))

    frame_data.mouse_pos = pygame.mouse.get_pos()
    frame_data.mouse_buttons = pygame.mouse.get_pressed()

    game_o.update_and_draw(frame_data, window)

    if frame_data.hovers:
        if cursor_img[1] is None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(cursor_img[1])
    else:
        if cursor_img[0] is None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            pygame.mouse.set_cursor(cursor_img[0])

    pygame.display.flip()

pygame.quit()