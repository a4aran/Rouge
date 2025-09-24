import pygame

import current_game_run_data
import gl_var
import window_size
from Illusion.frame_data_f import FrameData
from Illusion.go import GlobalObjects
from Illusion.helper import c_helper
from Illusion.importer import Importer, Assets, MusicManager
from Illusion.scene import Scene
from Illusion.ui import UI


class MainMenuSC(Scene):
    def __init__(self, importer: Importer, assets: Assets, music_manager: MusicManager, global_objects: GlobalObjects):
        super().__init__(importer, assets, music_manager, global_objects)

        self.fill_color = (255,150,150)

        temp = self.get_ui("default")

        text_r = global_objects.get_font("title_font")

        temp.new_text_display("test",text_r,(gl_var.window_center[0],150))
        temp2 = temp.get_text_display("test")
        temp2.set_all((0,0,0),90,["Title Title"])

        text_r = global_objects.get_font("text_font")
        temp.new_scene_change_button("game_btn",gl_var.window_center,gl_var.btn_size,global_objects.get_custom_object("btn_sprites"),2,delay=0.1)
        temp2 = temp.add_text_to_button("game_btn",text_r,"Play",50,(255,255,255))

class CharacterSelectionSC(Scene):
    def __init__(self, importer: Importer, assets: Assets, music_manager: MusicManager, global_objects: GlobalObjects):
        super().__init__(importer, assets, music_manager, global_objects)

        self.fill_color = (255,150,150)

        temp = self.get_ui("default")

        text_r = global_objects.get_font("title_font")

        temp.new_text_display("test",text_r,(gl_var.window_center[0],150))
        temp2 = temp.get_text_display("test")
        temp2.set_all((0,0,0),90,["Title Title"])

        temp_layout = window_size.width/6

        text_r = global_objects.get_font("text_font")
        temp.new_scene_change_button("new_game_btn",(temp_layout*2,window_size.height-100),gl_var.btn_size,global_objects.get_custom_object("btn_sprites"),3,delay=0.1)
        temp2 = temp.add_text_to_button("new_game_btn",text_r,"New Game",50,(255,255,255))
        temp.add_custom_button(LoadSaveBTN("load_save_btn",(temp_layout*4,window_size.height-100),gl_var.btn_size,global_objects.get_custom_object("btn_sprites"),3,delay=0.1))
        temp2 = temp.add_text_to_button("load_save_btn",text_r,"Load Save",50,(255,255,255))
        ui_data = temp.data()
        self.create_ui("character_change_btn_down")
        temp = self.get_ui("character_change_btn_down")
        temp.add_custom_button(
            ChangeCharacterBTN("character_down",(60,gl_var.window_center[1]),gl_var.vertical_btn_size,
                               global_objects.get_custom_object("vertical_btn_sprites"),-1,
                               delay=0.15)
        )
        temp.add_text_to_button("character_down",text_r,"<",150,(255,255,255))
        self.create_ui("character_change_btn_up")
        temp = self.get_ui("character_change_btn_up")
        temp.add_custom_button(
            ChangeCharacterBTN("character_up",(window_size.width-60,gl_var.window_center[1]),gl_var.vertical_btn_size,
                               global_objects.get_custom_object("vertical_btn_sprites"),1,
                               delay=0.15)
        )
        temp.add_text_to_button("character_up",text_r,">",150,(255,255,255))

        self.characters = 10
        self.character_page = 0

        for i in range(self.characters):
            self.create_ui(f"character_{i}")
            self.get_ui(f"character_{i}").new_text_display("test",text_r,gl_var.window_center)
            temp = self.get_ui(f"character_{i}").get_text_display("test")
            temp.set_all((0,0,0),70,[f"Character {i}"])

    def _update(self, frame_data: FrameData):
        self.get_ui("character_change_btn_down").should_show = self.character_page > 0
        self.get_ui("character_change_btn_up").should_show = self.character_page < self.characters - 1
        change_page = 0
        temp = self.get_ui("character_change_btn_down").data()
        if "change_page" in temp:
            if temp["change_page"] != 0:
                change_page = temp["change_page"]
                temp["change_page"] = 0
        temp = self.get_ui("character_change_btn_up").data()
        if change_page == 0:
            if "change_page" in temp:
                if temp["change_page"] != 0:
                    change_page = temp["change_page"]
                    temp["change_page"] = 0
        if change_page != 0:
            print(change_page)
            self.character_page = max(min(self.characters - 1,self.character_page+change_page),0)
            print(self.character_page)
        for i in range(self.characters):
            if i == self.character_page:
                self.get_ui(f"character_{i}").should_show = True
            else:
                self.get_ui(f"character_{i}").should_show = False

        super()._update(frame_data)

class ChangeCharacterBTN(c_helper.button_base()):
    def __init__(self, identifier: str, center_pos: pygame.Vector2, rect_size: tuple[float, float],
                 animated_sprite: list, character_calc: int, sound: pygame.mixer.Sound = [None,None], delay=None):
        super().__init__(identifier, center_pos, rect_size, animated_sprite, sound, delay)
        self.operation = character_calc

    def on_click(self, data:dict):
        super().on_click(data)
        print("click")
        data["change_page"] = self.operation

class LoadSaveBTN(c_helper.button_base()):
    def __init__(self, identifier: str, center_pos: pygame.Vector2, rect_size: tuple[float, float],
                 animated_sprite: list, scene_to_change_to: int, sound: pygame.mixer.Sound = [None,None], delay=None):
        super().__init__(identifier, center_pos, rect_size, animated_sprite, sound, delay)
        self.scene = scene_to_change_to

    def on_click(self, data: dict):
        super().on_click(data)
        if not data["should_change_scene"]:
            data["should_change_scene"] = True
            data["scene_to_change_to"] = self.scene
        current_game_run_data.cur_run_data.should_load_save = True


class RunOverSC(Scene):
    def __init__(self, importer: Importer, assets: Assets, music_manager: MusicManager, global_objects: GlobalObjects):
        super().__init__(importer, assets, music_manager, global_objects)
        self.fill_color = (0,0,0)

        temp = self.get_ui("default")

        text_r = global_objects.get_font("title_font")
        normal_font = global_objects.get_font("text_font")

        self.get_p_data = True

        temp.new_text_display("test",text_r,(gl_var.window_center[0],200))
        temp2 = temp.get_text_display("test")
        temp2.set_all((255,0,0),90,["Run Over"])
        temp.new_text_display("wave_info",normal_font,(gl_var.window_center[0],280))
        temp.get_text_display("wave_info").set_all((255,255,255),40,'')

        text_r = global_objects.get_font("text_font")
        temp.new_scene_change_button("main_scene_btn",(gl_var.window_center[0],gl_var.window_center[1] + 75),gl_var.btn_size,global_objects.get_custom_object("btn_sprites"),2,delay=0.1)
        temp.add_text_to_button("main_scene_btn",text_r,"Return",50,(255,255,255))

    def _update(self, frame_data: FrameData):
        super()._update(frame_data)
        if "previous_scene_data" in self.data:
            temp = self.get_ui("default").get_text_display("wave_info")
            if not temp.get_text() == f'Died on a wave {self.data["previous_scene_data"]['wave']}':
                temp.set_text([f'Died on wave {self.data["previous_scene_data"]['wave']}'])

    def on_changed_to(self,previous_scene_id):
        current_game_run_data.cur_run_data.reset()
        current_game_run_data.save_manager.reset()
