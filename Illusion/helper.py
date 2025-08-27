import pygame

from Illusion.frame_data_f import FrameData
from Illusion.ui import UI


class Helper:
    def __init__(self):
        pass

    @staticmethod
    def button_base():
        return UI._GUI.Button

    class Hoverable:
        def __init__(self):
            self.hoverbox = None

        def set_hoverbox(self,rect: pygame.Rect):
            self.hoverbox = rect

        def check_hovers(self,frame_data: FrameData):
            if isinstance(self.hoverbox,pygame.Rect):
                check = self.hoverbox.collidepoint(frame_data.mouse_pos)
                if check:
                    frame_data.hovers = True
                return check

c_helper = Helper()