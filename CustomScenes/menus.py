import gl_var
from Illusion.frame_data_f import FrameData
from Illusion.go import GlobalObjects
from Illusion.importer import Importer, Assets, MusicManager
from Illusion.scene import Scene


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
        temp.new_scene_change_button("main_scene_btn",(gl_var.window_center[0],gl_var.window_center[1] + 75),gl_var.btn_size,global_objects.get_custom_object("btn_sprites"),1,delay=0.1)
        temp.add_text_to_button("main_scene_btn",text_r,"Return",50,(255,255,255))

    def _update(self, frame_data: FrameData):
        if "previous_scene_data" in self.data:
            temp = self.get_ui("default").get_text_display("wave_info")
            if not temp.get_text() == f'Died on a wave {self.data["previous_scene_data"]['wave']}':
                temp.set_text([f'Died on wave {self.data["previous_scene_data"]['wave']}'])