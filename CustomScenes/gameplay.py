import c_objects.world
import gl_var
from Illusion.go import GlobalObjects
from Illusion.importer import Importer, Assets, MusicManager
from Illusion.scene import Scene


class GamePlaySC(Scene):
    def __init__(self, importer: Importer, assets: Assets, music_manager: MusicManager, global_objects: GlobalObjects):
        super().__init__(importer, assets, music_manager, global_objects)

        self.set_ui_to_background("default")
        temp = self.get_ui("default")
        temp.new_img(importer.get_sprite("gameplay_bg"),gl_var.window_center)

        self._objs.append(c_objects.world.World())