import ast
from collections.abc import Sequence

import pygame
from enum import Enum

from pygame import SRCALPHA

from Illusion.frame_data_f import FrameData
from Illusion.text_renderer import TextRenderer

class UI:
    def __init__(self,id):
        self.id = id
        self._hud = self._HUD()
        self._gui = self._GUI()
        self.should_show = True

    class _HUD:
        def __init__(self):
            self.surface_s = []

        class Parallax:
            def __init__(self,name: str, top_left:tuple[float,float],img: pygame.Surface,
                         speed: float,size: tuple[float,float],direction: int = 0,step: float = 0):
                self.name = name
                self.parallax_pos = pygame.Vector2(top_left)
                self.img_pos = 0
                self.img = img
                self.speed = speed
                self.parallax_window_size = size
                self.direction = direction
                self.carry = 0
                self.step = step

            def update(self,frame_data: FrameData):
                self.carry += self.speed * frame_data.dt
                if self.carry >= self.step:
                    self.img_pos += self.carry
                else:
                    return
                self.carry = 0
                axis_size = self.img.get_width()
                if self.direction == 2 or self.direction == 3:
                    axis_size = self.img.get_height()
                if self.img_pos >= axis_size: self.img_pos = 0

            def gen_frame(self):
                r_surf = pygame.Surface(self.parallax_window_size,SRCALPHA)
                if self.direction == 0 or self.direction == 1:
                    img_width = self.img.get_width()
                    repetitions = 2 + int(self.parallax_window_size[0] % img_width)
                    if self.direction == 0:
                        loc_pos = self.img_pos - img_width
                        for q in range(repetitions):
                            r_surf.blit(self.img,(loc_pos,0))
                            loc_pos += img_width
                    else:
                        loc_pos = r_surf.get_width() + img_width - self.img_pos
                        for q in range(repetitions):
                            r_surf.blit(self.img,(loc_pos,0))
                            loc_pos -= img_width

                elif self.direction == 2 or self.direction == 3:
                    img_height = self.img.get_height()
                    repetitions = 1 + int(self.parallax_window_size[1] % img_height)
                    if self.direction == 2:
                        loc_pos = self.img_pos - img_height
                        for q in range(repetitions):
                            r_surf.blit(self.img,(0,loc_pos))
                            loc_pos += img_height
                    else:
                        loc_pos = r_surf.get_width() + img_height - self.img_pos
                        for q in range(repetitions):
                            r_surf.blit(self.img,(0,loc_pos))
                            loc_pos -= img_height

                return  r_surf.convert_alpha()

            def draw(self,surface: pygame.Surface):
                surface.blit(self.gen_frame(), self.parallax_pos)

        class Img:
            def __init__(self,name: str,center_pos: tuple[float,float],img: pygame.Surface):
                self.name = name
                self.img = img.copy()
                self.pos = (center_pos[0] -self.img.get_width()/2,center_pos[1] -self.img.get_height()/2)
                self.no_calc_pos = center_pos

            def draw(self,surface: pygame.Surface):
                surface.blit(self.img,self.pos)

            def change_img(self,img: pygame.Surface):
                self.img = img
                self.pos = (self.no_calc_pos[0] -self.img.get_width()/2,self.no_calc_pos[1] -self.img.get_height()/2)

            def change_pos(self,center_pos: tuple[float,float]):
                self.no_calc_pos = center_pos
                self.pos = (self.no_calc_pos[0] -self.img.get_width()/2,self.no_calc_pos[1] -self.img.get_height()/2)

        class TextDisplay:
            def __init__(self,name: str,font: TextRenderer,center_pos: tuple[float,float]):
                self.name = name
                self.__center_pos = center_pos
                self.__top_left_pos = None
                self.__font = font
                self.__text = []
                self.__surface = None
                self.__size = None
                self.__color = (0, 0, 0)
                self.__should_reload = True
                self.__use_constant_y_pos = False
                self.__constant_y = 0

            def reload(self):
                if self.__text is not None and self.__size is not None and self.__color is not None:
                    size = [0,0]
                    lines_s = []
                    for line in self.__text:
                        temp = self.__font.render(line, self.__size, self.__color).convert_alpha()
                        lines_s.append(temp)
                        size[1] += temp.get_height()
                        size[0] = max(size[0],temp.get_width())
                    self.__surface = pygame.Surface(size,SRCALPHA)
                    y_pos = 0
                    for surf in lines_s:
                        l_x_pos = size[0]/2 - surf.get_width()/2
                        self.__surface.blit(surf,(l_x_pos,y_pos))
                        y_pos += surf.get_height()
                    self.__top_left_pos = (self.__center_pos[0] - self.__surface.get_width() / 2,
                           self.__center_pos[1] - self.__surface.get_height() / 2)
                    self.__should_reload = False
                else:
                    raise AttributeError("Lack of attributes Text || Size || Color")

            def add_line(self, text: str):
                self.__text.append(text)
                self.__should_reload = True

            def change_line(self,line_number: int, text:str):
                self.__text[line_number] = text
                self.__should_reload = True

            def delete_line(self,line_number: int):
                self.__text.pop(line_number)
                self.__should_reload = True

            def set_size(self, size: int):
                self.__size = size
                self.__should_reload = True

            def set_color(self,color: tuple[int,int,int]):
                self.__color = color
                self.__should_reload = True

            def set_pos(self,center_pos: tuple[float,float]):
                self.__center_pos =center_pos

            def change_properties(self, color: tuple[int,int,int] = None, center_pos: tuple[float,float] = None, size: int = None):
                if color is not None: self.__color = color
                if center_pos is not None: self.__center_pos = center_pos
                if size is not None: self.__size = size
                self.__should_reload = True

            def set_all(self, color: tuple[int,int,int], size: int, text: list[str]):
                self.__color = color
                self.__size = size
                self.__text = text
                self.__should_reload = True

            def set_text(self,text: list[str]):
                self.__text = text
                self.__should_reload = True

            def draw(self,surface: pygame.Surface):
                if self.__should_reload: self.reload()
                r_pos = self.__top_left_pos
                if self.__use_constant_y_pos:
                    r_pos = (self.__top_left_pos[0],self.__constant_y)
                surface.blit(self.__surface,r_pos)

            def toggle_constant_y_pos(self):
                self.__use_constant_y_pos = True

            def set_constant_y_pos(self,y:float):
                self.__constant_y = y

            def get_text(self):
                return self.__text

        class FormattedTextDisplay:
            def __init__(self,name: str,fonts: dict,center_pos: tuple[float,float]):
                self.name = name
                self.__center_pos = center_pos
                self.__top_left_pos = None
                self.__fonts = fonts
                self.__unformatted_text = []
                self.__formatted_text = []
                self.__surface = None
                self.__should_reload = True
                self.__use_constant_y_pos = False
                self.__constant_y = 0

            def set_text(self,text: Sequence[str]):
                self.__unformatted_text = text
                self.__should_reload = True

            def __format(self):
                temp_surf_list = []

                nums = "1234567890"
                color_chars = f"{nums},()"
                font_exceptions = ";{}:"

                reading_formatting = False
                reading_text = False

                text = ""

                setting_size = False
                setting_color = False
                setting_font = False

                cur_size = None
                cur_color = None
                cur_font = None
                for line in self.__unformatted_text:
                    temp = []
                    for letter in line:
                        if reading_formatting:
                            if setting_size and letter in nums:
                                cur_size = int(f"{cur_size}{letter}")
                            if setting_color and letter in color_chars:
                                cur_color = f"{cur_color}{letter}"
                            if setting_font and letter not in font_exceptions:
                                cur_font = f"{cur_font}{letter}"

                            if letter == "s":
                                setting_size = True
                                cur_size = ""
                            if letter == "c":
                                setting_color = True
                                cur_color = ""
                            if letter == "f":
                                setting_font = True
                                cur_font = ""

                            if letter == ";":
                                setting_color = False
                                setting_size = False
                                setting_font = False

                            if letter == "}":
                                reading_formatting = False
                                reading_text = True
                        if letter == "{":
                            reading_formatting = True
                            reading_text = False
                            # don’t reset here!
                            text_to_render = text
                            text = ""
                            if text_to_render:
                                # flush previous text chunk before formatting
                                if cur_size is None: cur_size = 24
                                if cur_color is None: cur_color = (0, 0, 0)
                                if cur_font is None: cur_font = next(iter(self.__fonts.keys()))
                                temp.append(
                                    self.__gen_for_surf(text_to_render, self.__fonts[cur_font], cur_size, cur_color))
                        if not reading_formatting and reading_text:
                            if letter != "}":
                                text += letter
                        if letter == "}":
                            reading_formatting = False
                            reading_text = True
                            if cur_size in ("", None): cur_size = 24
                            if cur_color in ("", None): cur_color = (0, 0, 0)
                            if isinstance(cur_color, str): cur_color = ast.literal_eval(cur_color)
                            if cur_font in ("", None): cur_font = next(iter(self.__fonts.keys()))

                    # only append the finished line here, not inside the inner loop
                    if text:
                        # flush any leftover text into a surface
                        if cur_size == "" or cur_size is None: cur_size = 24
                        if cur_color == "" or cur_color is None: cur_color = "(0,0,0)"
                        if cur_font == "" or cur_font is None: cur_font = next(iter(self.__fonts.keys()))
                        if not isinstance(cur_color,tuple): cur_color = ast.literal_eval(cur_color)
                        temp.append(self.__gen_for_surf(text, self.__fonts[cur_font], cur_size, cur_color))
                        text = ""

                    temp_surf_list.append(temp)
                total_width = 0
                part_width = []
                total_line_width = []
                for surf_list in temp_surf_list:
                    temp = []
                    total = 0
                    for surf in surf_list:
                        temp.append(surf.get_width())
                        total += surf.get_width()
                    total_line_width.append(total)
                    total_width = max(total_width,total)
                line_height_list = []
                total_height = 0
                for surf_list in temp_surf_list:
                    max_height = 0
                    for surf in surf_list:
                        max_height = max(max_height,surf.get_height())
                    total_height += max_height
                    line_height_list.append(max_height)
                line_surfaces = []
                for num, line in enumerate(temp_surf_list):
                    temp = pygame.Surface((total_width,line_height_list[num]),pygame.SRCALPHA)
                    calc_x = total_width/2 - total_line_width[num]/2
                    for surf in temp_surf_list[num]:
                        temp.blit(surf,(calc_x,0))
                        calc_x += surf.get_width()
                    line_surfaces.append(temp)

                final_surf = pygame.Surface((total_width,total_height),pygame.SRCALPHA)
                blit_height = 0
                for surf in line_surfaces:
                    final_surf.blit(surf,(0,blit_height))
                    blit_height += surf.get_height()

                self.__surface = final_surf

            @staticmethod
            def __gen_for_surf(text:str,font: TextRenderer,size:int,color: tuple[int,int,int]):
                return font.render(text,size,color,True)

            def reload(self):
                self.__format()
                if not self.__unformatted_text: self.__surface = pygame.Surface((1,1),pygame.SRCALPHA)
                self.__top_left_pos = (self.__center_pos[0] - self.__surface.get_width()/2,
                                     self.__center_pos[1] - self.__surface.get_height()/2,)

            def draw(self,surface: pygame.Surface):
                if self.__should_reload: self.reload()
                r_pos = self.__top_left_pos
                if self.__use_constant_y_pos:
                    r_pos = (self.__top_left_pos[0],self.__constant_y)
                surface.blit(self.__surface,r_pos)

            def set_pos(self,center_pos: tuple[float,float]):
                self.__center_pos =center_pos

            def toggle_constant_y_pos(self):
                self.__use_constant_y_pos = True

            def set_constant_y_pos(self,y:float):
                self.__constant_y = y

        class Animation:
            def __init__(self,name: str,center_pos: tuple[float,float],sprites: list,fps:int,play_amount:int = 0):
                self.name = name
                self.sprites = sprites.copy()
                self.c_pos = center_pos
                self.frame_time = [-0.05,1 / fps]
                self.current_frame = 0
                self.repetition_count = 0
                self.play_count = [play_amount,False]

            def update(self,frame_data: FrameData):
                if not self.play_count[1]:
                    self.frame_time[0] += frame_data.dt
                    if self.frame_time[1] < self.frame_time[0]:
                        self.current_frame += 1
                        if self.current_frame == len(self.sprites):
                            self.repetition_count += 1
                            self.current_frame = 0
                            if self.play_count[0] != 0:
                                if self.repetition_count == self.play_count[0]:
                                    self.play_count[1] = True
                                    self.current_frame = len(self.sprites) - 1
                        self.frame_time[0] = 0

            def draw(self,surface: pygame.Surface):
                r = self.sprites[self.current_frame].get_rect()
                r.center = self.c_pos
                surface.blit(self.sprites[self.current_frame],
                             r.topleft
                             )

            def is_done(self):
                return self.play_count[1]

        def add_img(self,img: pygame.Surface):
            self.surface_s.append(img)

        def draw(self, surface: pygame.Surface):
            for s in self.surface_s:
                s.draw(surface)

        def update(self,frame_data: FrameData):
            for surface in self.surface_s:
                if isinstance(surface,self.Animation) or isinstance(surface,self.Parallax):
                    surface.update(frame_data)

        def find_animation(self,name:str):
            i = None
            for index, a in enumerate(self.surface_s):
                if isinstance(a, self.Animation):
                    if a.name == name:
                        i = index
            if i is None:
                print("'"+name+"' animation not found")
                return
            return self.surface_s[i]

        def find_text_display(self,name:str):
            i = None
            for index, a in enumerate(self.surface_s):
                if isinstance(a, self.TextDisplay):
                    if a.name == name:
                        i = index
            if i is None:
                print("'"+name+"' text display not found")
                return
            return self.surface_s[i]

        def find_img(self,name:str): #add
            i = None
            for index, a in enumerate(self.surface_s):
                if isinstance(a, self.Img):
                    if a.name == name:
                        i = index
            if i is None:
                print("'"+name+"' image not found")
                return
            return self.surface_s[i]

        def find_formatted_text_display(self,name:str):
            i = None
            for index, a in enumerate(self.surface_s):
                if isinstance(a, self.FormattedTextDisplay):
                    if a.name == name:
                        i = index
            if i is None:
                print("'"+name+"' formatted text display not found")
                return
            return self.surface_s[i]


    class _GUI:
        def __init__(self):
            self.buttons = []
            self.data = {}
            self.clear_data()

        def clear_data(self):
            self.data = {
                "should_change_scene": False,
                "scene_to_change_to": 0
            }

        class Button:
            class State(Enum):
                DEFAULT = 0
                HOVERED = 1
                PRESSED = 2

            def __init__(self, identifier: str, center_pos: pygame.Vector2, rect_size: tuple[float,float], animated_sprite: list,
                         sound: list[pygame.mixer.Sound,pygame.mixer.Sound] = [None,None], delay:float = None):
                self.identifier = identifier
                self.rect = pygame.Rect((0,0),rect_size)
                self.rect.center = center_pos
                self.current_state = self.State.DEFAULT
                self.frames = animated_sprite
                self.sounds = sound
                self.delay = [0,delay,False]
                self.lag_frame = False
                self.text_surface = [None,None,None]

            def update(self, frame_data: FrameData, data: dict):
                if not self.delay[2]:  # If delay not started, check for hover/click
                    self.current_state = self.State.DEFAULT
                    if self.rect.collidepoint(frame_data.mouse_pos):
                        if frame_data.mbtn_just_pressed[0]:
                            self.current_state = self.State.PRESSED
                            self.delay[2] = True  # Start the delay
                            self.lag_frame = True
                            if self.sounds[1] is not None and not self.lag_frame:
                                self.sounds[1].play()
                        else:
                            self.current_state = self.State.HOVERED
                else:
                    # Delay already started — maintain visual feedback and accumulate time
                    self.current_state = self.State.PRESSED
                    if self.delay[1] is not None:
                        self.delay[0] += frame_data.dt
                        if self.delay[0] > self.delay[1]:
                            self.on_click(data)
                            self.reset()
                    else:
                        self.on_click(data)
                        self.reset()
                if self.current_state == self.State.HOVERED:
                    frame_data.hovers = True
                self.lag_frame = False

            def reset(self):
                d = [
                    0,
                    self.delay[1],
                    False
                ]
                self.delay = d

            def on_click(self, data:dict):
                if self.sounds[0] is not None:
                    self.sounds[0].play()

            def draw(self,surface: pygame.Surface):
                surface.blit(self.frames[self.current_state.value],self.rect.topleft)
                if self.text_surface[self.current_state.value] is not None:
                    dest_ = (
                        self.rect.center[0] - self.text_surface[self.current_state.value].get_width()/2,
                        self.rect.center[1] - self.text_surface[self.current_state.value].get_height()/2
                    )
                    surface.blit(self.text_surface[self.current_state.value],dest_)

            def add_text(self,text_renderer: TextRenderer ,text: str, size: int, color: tuple[int,int,int]):
                self.text_surface = [
                    text_renderer.render(text,size,color),
                    text_renderer.render(text,size,color),
                    text_renderer.render(text,size,color)
                ]

            def modify_default_text(self,text_renderer: TextRenderer ,text: str, size: int, color: tuple[int,int,int]):
                self.text_surface[0] = text_renderer.render(text,size,color)

            def modify_hover_text(self,text_renderer: TextRenderer ,text: str, size: int, color: tuple[int,int,int]):
                self.text_surface[1] = text_renderer.render(text,size,color)

            def modify_pressed_text(self,text_renderer: TextRenderer ,text: str, size: int, color: tuple[int,int,int]):
                self.text_surface[2] = text_renderer.render(text,size,color)

        class ChangeScButton(Button):
            def __init__(self, identifier: str, center_pos: pygame.Vector2, rect_size: tuple[float, float],
                         animated_sprite: list, scene_to_change_to: int, sound: pygame.mixer.Sound = None, delay=None):
                super().__init__(identifier, center_pos, rect_size, animated_sprite, sound, delay)
                self.scene = scene_to_change_to

            def on_click(self, data:dict):
                super().on_click(data)
                if not data["should_change_scene"]:
                    data["should_change_scene"] = True
                    data["scene_to_change_to"] = self.scene

        def update(self,frame_data: FrameData):
            for button in self.buttons:
                button.update(frame_data,self.data)

        def draw(self,surface: pygame.Surface):
            for button in self.buttons:
                button.draw(surface)

        def find_button(self, name:str) -> Button:
            for butt in self.buttons:
                if butt.identifier == name:
                    return butt

    def add_custom_button(self, button: _GUI.Button):
        self._gui.buttons.append(button)

    def new_scene_change_button(self,identifier: str, center_pos: pygame.Vector2,size: tuple[float,float],sprites: list,scene_to_change_to,sound: pygame.mixer.Sound = [None,None],delay: float = None):
        self._gui.buttons.append(
            self._gui.ChangeScButton(
                identifier,
                center_pos,
                size,
                sprites,
                scene_to_change_to,
                sound,
                delay,
            )
        )

    def add_text_to_button(self,button_name: str,text_renderer: TextRenderer ,text: str, size: int, color: tuple[int,int,int]):
        temp = self._gui.find_button(button_name)
        temp.add_text(text_renderer,text,size,color)

    def modify_button_text(self,button_name: str,button_state: int,text_renderer: TextRenderer ,text: str, size: int, color: tuple[int,int,int]):
        if not 3 >= button_state >= 0: raise KeyError("Button State out of bounds")
        temp = self._gui.find_button(button_name)
        if button_state == 0: temp.modify_default_text(text_renderer,text,size,color)
        if button_state == 1: temp.modify_hover_text(text_renderer,text,size,color)
        if button_state == 2: temp.modify_pressed_text(text_renderer,text,size,color)

    def new_img(self,name:str,img: pygame.Surface,center_pos: pygame.Vector2):
        self._hud.surface_s.append(
            self._hud.Img(
                name,
                center_pos, img
            )
        )

    def new_animation(self,name:str,sprites: list,center_pos: pygame.Vector2,fps:int,play_count: int = 0):
        self._hud.surface_s.append(
            self._hud.Animation(
                name,
                center_pos,
                sprites,
                fps,
                play_count
            )
        )

    def new_parallax(self, name:str,top_left:tuple[float,float],img: pygame.Surface,speed: float, size: tuple[float,float],direction: int = 0,step: float = 0):
        self._hud.surface_s.append(
            self._hud.Parallax(
                name,top_left, img, speed, size,direction, step
            )
        )

    def new_text_display(self, name: str,text_renderer: TextRenderer, center_pos: tuple[float,float]):
        self._hud.surface_s.append(
            self._hud.TextDisplay(
                name,
                text_renderer,
                center_pos
            )
        )

    def new_formatted_text_display(self, name: str,fonts: dict[TextRenderer], center_pos: tuple[float,float]):
        self._hud.surface_s.append(
            self._hud.FormattedTextDisplay(
                name,
                fonts,
                center_pos
            )
        )

    def get_text_display(self,name: str) -> _HUD.TextDisplay:
        return  self._hud.find_text_display(name)

    def get_formatted_text_display(self,name: str) -> _HUD.FormattedTextDisplay:
        return  self._hud.find_formatted_text_display(name)

    def get_animation(self,name:str):
        return  self._hud.find_animation(name)

    def get_img(self,name:str) -> _HUD.Img: #add
        return self._hud.find_img(name)

    def update(self,frame_data: FrameData):
        self._hud.update(frame_data)
        self._gui.update(frame_data)

    def draw(self,surface: pygame.Surface):
        self._hud.draw(surface)
        self._gui.draw(surface)

    def get_gui(self):
        return self._GUI

    def data(self):
        return self._gui.data

    def reset_data(self):
        self._gui.clear_data()

    def delete_var_from_data(self,var_name: str):
        if var_name in self._gui.data:
            self._gui.data.pop(var_name)
        else:
            print("No variable " + var_name + " in data")

    def modify_parallax(self,parallax_name: str,speed = None, stepping = None, direction = None):
        for par in self._hud.surface_s:
            if isinstance(par, self._HUD.Parallax) and par.name == parallax_name:
                if speed is not None: par.speed = speed
                if stepping is not None: par.step = stepping
                if direction is not None: par.direction = direction