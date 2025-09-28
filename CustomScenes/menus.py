import pygame

import characters
import current_game_run_data
import gl_var
import window_size
from Illusion import helper
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

        title_font = global_objects.get_font("title_font")
        temp_layout = window_size.width/6

        text_r = global_objects.get_font("text_font")
        temp.add_custom_button(NewSaveBTN("new_save_btn",(temp_layout*2,window_size.height-100),gl_var.btn_size,global_objects.get_custom_object("btn_sprites"),delay=0.1))
        temp.add_text_to_button("new_save_btn",text_r,"New Game",50,(255,255,255))
        temp.add_custom_button(LoadSaveBTN("load_save_btn",(temp_layout*4,window_size.height-100),gl_var.btn_size,global_objects.get_custom_object("btn_sprites"),3,delay=0.1))
        temp.add_text_to_button("load_save_btn",text_r,"Load Save",50,(255,255,255))
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

        self.characters = len(characters.characters)
        self.character_page = 0

        for i in range(self.characters):
            font_dict = {
                "def": text_r,
                "title": title_font
            }

            self.create_ui(f"character_{i}")
            x_pos = gl_var.window_center[0]/2 * 3 - 40
            temp_ui = self.get_ui(f"character_{i}")

            temp_ui.new_img("icon",global_objects.get_custom_object(f"{characters.characters[i]["name"]}_icon"),(gl_var.window_center[0]/3 * 2,gl_var.window_center[1]))

            capitalized_name = characters.characters[i]["name"].capitalize()
            title_size = 90 if len(capitalized_name) < 15 else 70

            temp_ui.new_text_display("title", title_font, (gl_var.window_center[0], 80))
            temp_ui.get_text_display("title").set_all((0, 0, 0), title_size, [capitalized_name])

            temp_ui.new_formatted_text_display("stats",font_dict,(x_pos,0))
            temp = temp_ui.get_formatted_text_display("stats")
            temp.toggle_constant_y_pos()
            temp.set_constant_y_pos(130)
            temp_stats_dict = characters.characters[i]["base_stats"]
            temp_ability_dict = characters.characters[i]["ability"]
            deafult_formatting = "{s:30;c:(50,50,50);f:def}"
            ability_name_size = 55 - (max(len(temp_ability_dict["name"])-5,0))*6
            text_list = [
                f"{{s:55;c:(255,255,255);f:title}}STATS",
                f"{deafult_formatting}Max HP: {temp_stats_dict['max_hp']}",
                f"Speed: {temp_stats_dict['speed']}",
                f"Damage: {temp_stats_dict['attack_dmg']}",
                f"Firerate: {temp_stats_dict['firerate']}",
                f"Pierce: {temp_stats_dict['pierce']}",
                helper.to_format_string((50,50,50),25,"def",f"Bullet Speed: {temp_stats_dict['b_speed']}"),
                f" ",
                "{{s:15;c:(0,0,0);f:def}}ABILITY",
                f"{{s:{ability_name_size};c:(255,255,255);f:title}}{temp_ability_dict['name'].upper()}"
            ]
            if temp_ability_dict["type"] == "activated":
                text_list.append(f"{deafult_formatting}Type: Activated")
                text_list.append(f"Cooldown: {temp_ability_dict['cooldown'][1]}s")
                if "active" in temp_ability_dict:
                    text_list.append(
                        f"Active for: {temp_ability_dict['active'][1]}s"
                    )
            text_list.append(f" ")
            text_list.append(f" ")
            temp.set_text(text_list)


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

        if "global_character_change" in self.get_ui("default").data() and self.get_ui("default").data()["global_character_change"]:
            self.get_ui("default").data().pop("global_character_change")
            current_game_run_data.cur_run_data.selected_character = self.character_page
            self.edit_change_scene_data(True,3)

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

class NewSaveBTN(c_helper.button_base()):
    def __init__(self, identifier: str, center_pos: pygame.Vector2, rect_size: tuple[float, float],
                 animated_sprite: list, sound: pygame.mixer.Sound = [None,None], delay=None):
        super().__init__(identifier, center_pos, rect_size, animated_sprite, sound, delay)

    def on_click(self, data: dict):
        super().on_click(data)
        data["global_character_change"] = True

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
