class FrameData:
    def __init__(self):
        self.dt: float = 0.0
        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_buttons: tuple[bool, bool, bool] = (False, False, False)
        self.mbtn_just_pressed: list[bool] = [False, False, False]
        self.keys = None
        self.hovers = False

    def reset_mbtn(self):
        self.mbtn_just_pressed = [False, False, False]