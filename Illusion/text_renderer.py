import pygame


class TextRenderer:
    def __init__(self, font_name: str,font_prefix: str):
        self.font_path = font_prefix + font_name
        self.fonts_by_size = {}

    def get_font(self, size: int) -> pygame.font.Font:
        if size not in self.fonts_by_size:
            try:
                self.fonts_by_size[size] = pygame.font.Font(self.font_path, size)
            except:
                self.fonts_by_size[size] = pygame.font.Font("." + self.font_path, size)
        return self.fonts_by_size[size]

    def render(self, text: str, size: int = 24, color: tuple = (0, 0, 0), antialias: bool = True) -> pygame.Surface:
        font = self.get_font(size)
        return font.render(text, False, color)