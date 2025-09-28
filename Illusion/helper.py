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

    class Timer:
        def __init__(self,time:float):
            self._countdown = 0
            self._full_time = time
            self.running = False

        def start(self):
            self.running = True

        def update(self,dt:float):
            if self.running:
                self._countdown += dt
                if self._countdown >= self._full_time:
                    self._countdown = 0
                    self.running = False

        def change_time(self,new_time: float):
            self._full_time = new_time

        def change_countdown(self,countdown: float):
            self._countdown = countdown

        def is_counting_down(self):
            return self.running

        def reset(self):
            self._countdown = 0
            self.running = False

        def get_completion_percentage(self):
            if not self.running:
                return 1
            else:
                return self._countdown / self._full_time

        def get_time_left(self):
            return max(0, self._full_time - self._countdown)

def to_format_string(color: tuple[int,int,int],size: int, font_name: str, text: str):
    return f"{{s:{size};c:{color};f:{font_name};}}{text}"

c_helper = Helper()