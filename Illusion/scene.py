import pygame

from Illusion import ui
from Illusion.frame_data_f import FrameData
from Illusion.go import GlobalObjects
from Illusion.importer import Importer, Assets, MusicManager


class Scene:
    def __init__(self,importer: Importer,assets: Assets,music_manager: MusicManager,global_objects: GlobalObjects):
        self._objs = []
        self._uis = {}
        self._bg_uis = {}
        self.create_ui("default")
        self.data = {}
        self.__clear_data()
        self.fill_color = (0,0,0)
        self._music_manager = music_manager

    def _update(self, frame_data: FrameData):
        self.get_data_from_uis()
        for o in self._objs:
            o.update(frame_data)
        for ui in self._uis:
            temp = self.get_ui(ui)
            if temp.should_show:
                temp.update(frame_data)
        for bg_ui in self._bg_uis:
            temp = self.get_ui(bg_ui)
            if temp.should_show:
                temp.update(frame_data)

    def _draw(self,surface: pygame.Surface): #unprivate
        for bg in self._bg_uis:
            temp = self.get_ui(bg)
            if temp.should_show:
                temp.draw(surface)
        for o in self._objs:
            o.draw(surface)
        for ui in self._uis:
            temp = self.get_ui(ui)
            if temp.should_show:
                temp.draw(surface)

    def update_and_draw(self,frame_data: FrameData,surface: pygame.Surface):
        surface.fill(self.fill_color)
        self._update(frame_data)
        self._draw(surface)

    def on_changed_from(self):
        self.__clear_data()

    def on_changed_to(self,previous_scene_id):
        pass

    def __clear_data(self):
        self.data["should_change_scene"] = False
        self.data["scene_to_change_to"] = 0

    def edit_change_scene_data(self,should_change:bool,scene_to_change_to:int):
        self.data["should_change_scene"] = should_change
        self.data["scene_to_change_to"] = scene_to_change_to

    def get_data_from_uis(self):
        for ui in self._uis:
            temp = self.get_ui(ui)
            if temp.should_show:
                if temp.data()["should_change_scene"]:
                    self.edit_change_scene_data(temp.data()["should_change_scene"],temp.data()["scene_to_change_to"])
                    temp.reset_data()
                    return
        for bg_ui in self._bg_uis:
            temp = self.get_ui(bg_ui)
            if temp.should_show:
                if temp.data()["should_change_scene"]:
                    self.edit_change_scene_data(temp.data()["should_change_scene"],temp.data()["scene_to_change_to"])
                    temp.reset_data()
                    return

    def create_ui(self,ui_name):
        self._uis[ui_name] = ui.UI(ui_name)

    def get_ui(self, ui_name) -> ui.UI:
        if ui_name in self._uis:
            return self._uis[ui_name]
        if ui_name in self._bg_uis:
            return self._bg_uis[ui_name]
        print(f"UI '{ui_name}' not found in either active or background UIs")
        return None

    def delete_ui(self,ui_name: str):
        if ui_name in self._uis:
            self._uis.pop(ui_name)
            return
        elif ui_name in self._bg_uis:
            self._uis.pop(ui_name)
            return
        print("Ui " + ui_name + " not found")

    def add_ui(self,ui: ui.UI):
        self._uis[ui.id] = ui

    def set_ui_to_background(self, name: str):
        ui_v = self._uis.pop(name, None)
        if ui_v:
            self._bg_uis[name] = ui_v
        else:
            print(f"UI '{name}' not found in active UI dict")

    def set_background_to_ui(self, name: str):
        bg_ui = self._bg_uis.pop(name, None)
        if bg_ui:
            self._uis[name] = bg_ui
        else:
            print(f"UI '{name}' not found in background UI dict")