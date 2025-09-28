from Illusion.text_renderer import TextRenderer
from Illusion.ui import UI
import pygame.font

class GlobalObjects:
    def __init__(self):
        self.__uis = {}
        self.__fonts = {}
        self.font_prefix = "../assets/fonts/"
        self.__custom_objects = {}

    def add_ui(self,ui: UI):
        self.__uis[ui.id] = ui

    def get_ui(self,ui_name) -> UI:
        if ui_name in self.__uis: return  self.__uis[ui_name]
        else: raise KeyError(f"UI {ui_name} not found")

    def delete_ui(self,ui_name):
        self.__uis.pop(ui_name)

    def add_font(self,font_name: str,font_file:str):
        self.__fonts[font_name] = TextRenderer(font_file, self.font_prefix)

    def get_font(self, font_name: str) -> TextRenderer:
        if font_name in self.__fonts: return  self.__fonts[font_name]
        else: raise KeyError(f"TextRenderer {font_name} not found")

    def render_text(self,font_name: str,text: str, size: int, color: tuple = (0, 0, 0)):
        if font_name in self.__fonts: return self.__fonts[font_name].render(text,size,color)
        else: raise KeyError(f"Font {font_name} not found")

    def add_custom_object(self,name: str,c_object):
        self.__custom_objects[name] = c_object

    def get_custom_object(self,name:str):
        if name in self.__custom_objects: return  self.__custom_objects[name]
        else: raise KeyError(f"Custom Object {name} not found")

    def delete_custom_object(self,name:str):
        self.__custom_objects.pop(name)