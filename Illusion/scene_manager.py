import pygame

import Illusion.engine_constants as g
from Illusion.scene import Scene
from Illusion.frame_data_f import FrameData


class SceneManager:
    def __init__(self):
        self.__scenes = []
        self.__active_scene = g.SC_LOAD
        self.__sc_data = {}
        self.__previous_scene = 0
        self.__previous_scene_data = {}

    def update_and_draw(self,frame_data: FrameData,surface: pygame.Surface):
        self.__get_data_from_scene()
        if self.__sc_data["should_change_scene"]:
            self.change_scene(self.__sc_data["scene_to_change_to"])
        if hasattr(self.__scenes[self.__active_scene],"get_p_data") and self.__scenes[self.__active_scene].get_p_data:
            self.__scenes[self.__active_scene].data["previous_scene_data"] = self.__previous_scene_data
            self.__scenes[self.__active_scene].get_p_data = False
        self.__scenes[self.__active_scene].update_and_draw(frame_data,surface)

    def __get_data_from_scene(self):
        self.__sc_data = self.__scenes[self.__active_scene].data

    def change_scene(self, scene_id: int):
        self.__scenes[self.__active_scene].on_changed_from()
        self.__previous_scene = self.__active_scene
        self.__previous_scene_data = self.__sc_data
        self.__active_scene = scene_id
        self.__scenes[self.__active_scene].on_changed_to(self.__previous_scene)

    def add_scene(self,scene: Scene):
        self.__scenes.append(scene)

