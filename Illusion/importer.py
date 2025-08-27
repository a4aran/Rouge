import pygame.image

class Importer:
    def __init__(self,hws: bool):
        self.__sprites = {}
        self.__animated_sprites = {}
        self.__sounds = {}
        self.__hws = hws

        self.__prefix = [
            '',  # image prefix
            '',  # animated sprite prefix
            ''   # sound prefix
        ]

    def import_img(self, name: str, path: str, result_size: tuple[int, int] | int):
        self.__sprites[name] = self.return_import_img(path,result_size)

    def import_animated_sprite(self, name: str, path: str, frames_amount: int,
                               result_frame_size: tuple[int, int] | float):
        self.__animated_sprites[name] = self.return_import_animated_sprite(path,frames_amount,result_frame_size)

    def import_sound(self, name: str, path: str):
        if self.__hws:
            try:
                self.__sounds[name] = pygame.mixer.Sound(self.__prefix[2] + path)
            except:
                self.__sounds[name] = pygame.mixer.Sound("." + self.__prefix[2] + path)

    def get_sprite(self, name: str):
        return self.__sprites[name]

    def get_animated_sprite(self, name: str):
        return self.__animated_sprites[name]

    def get_sound(self, name: str):
        if self.__hws:
            return self.__sounds[name]

    def play_sound(self,name):
        if self.__hws:
            self.__sounds[name].play()

    def set_img_prefix(self, path_prefix: str):
        self.__prefix[0] = path_prefix

    def set_animated_sprite_prefix(self, path_prefix: str):
        self.__prefix[1] = path_prefix

    def set_sound_prefix(self, path_prefix: str):
        self.__prefix[2] = path_prefix

    def return_import_img(self, path: str, result_size: tuple[int, int] | int):
        try:
            src_img = pygame.image.load(self.__prefix[0] + path).convert_alpha()
        except:
            src_img = pygame.image.load("." + self.__prefix[0] + path).convert_alpha()

        if isinstance(result_size, tuple):
            img = pygame.transform.scale(src_img, result_size)
        else:
            rs = (
                src_img.get_width() * result_size,
                src_img.get_height() * result_size
            )
            img = pygame.transform.scale(src_img, rs)
        return  img

    def return_import_animated_sprite(self, path: str, frames_amount: int,
                               result_frame_size: tuple[int, int] | float):
        try:
            src_img = pygame.image.load(self.__prefix[1] + path).convert_alpha()
        except:
            src_img = pygame.image.load("." + self.__prefix[1] + path).convert_alpha()

        if isinstance(result_frame_size, tuple):
            rfs = result_frame_size
            width = frames_amount * rfs[0]
            height = rfs[1]
        else:
            scale = result_frame_size
            rfs = (
                int(src_img.get_width() / frames_amount * scale),
                int(src_img.get_height() * scale)
            )
            width = frames_amount * rfs[0]
            height = rfs[1]

        img = pygame.transform.scale(src_img, (width, height))

        frames = []
        for f in range(frames_amount):
            frame = pygame.Surface(rfs, pygame.SRCALPHA)
            frame.blit(img, (0, 0), (f * rfs[0], 0, *rfs))
            frames.append(frame)

        return frames

class Assets:
    def __init__(self):
        self.__sprites = {}
        self.__animated_sprites = {}

    def add_sprite(self,name: str,sprite: pygame.Surface):
        self.__sprites[name] = sprite

    def add_animated_sprite(self,name:str,sprites: list):
        self.__animated_sprites[name] = sprites

    def add_frame_to_animated_sprite(self,sprite_name: str,frame: pygame.Surface):
        if sprite_name in self.__animated_sprites:
            self.__animated_sprites[sprite_name].append(frame)
        else:
            print("Assets: Can't add " + str(frame) + ", '" + sprite_name + "' doesn't exist")

    def get_sprite(self,name:str):
        return self.__sprites[name]

    def get_animated_sprites(self,name:str):
        return self.__animated_sprites[name]

class MusicManager:
    def __init__(self,hws):
        self._tracks = {}
        self._current_track = None
        self._prefix = ""
        self._volume = 100
        self._mute = False
        self.__hws = hws

    def add_track(self,name: str, path: str):
        if not self.__hws: return
        self._tracks[name] = self._prefix + path

    def remove_track(self,name: str):
        if not self.__hws: return
        self._tracks.pop(name)

    def play_track(self,name:str):
        if not self.__hws: return
        if not name in self._tracks:
            print("Couldn't find track")
            return
        pygame.mixer.music.unload()
        try:
            pygame.mixer.music.load(self._tracks[name])
        except:
            pygame.mixer.music.load("." + self._tracks[name])

        self._current_track = name
        pygame.mixer.music.play(-1)
        self.resync_volume()

    def set_path_prefix(self,prefix: str):
        if not self.__hws: return
        self._prefix = prefix

    def unload_all(self):
        if not self.__hws: return
        pygame.mixer.music.unload()
        self._current_track = None

    def pause(self):
        if not self.__hws: return
        pygame.mixer.music.pause()

    def unpause(self):
        if not self.__hws: return
        pygame.mixer.music.unpause()

    def set_volume(self,amount: int):
        if not self.__hws: return
        self._volume = max(min(amount,100),0)
        self.resync_volume()

    def change_volume_by(self,amount: int): # if you wanna decrease the volume enter negative number
        if not self.__hws: return
        self._volume += amount
        self._volume = max(min(self._volume, 100), 0)
        self.resync_volume()

    def get_volume_value(self):
        if not self.__hws: return
        return self._volume

    def toggle_mute(self):
        if not self.__hws: return
        self._mute = not self._mute
        self.resync_volume()

    def resync_volume(self):
        if not self.__hws: return
        if self._mute:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self._volume / 100)

    def get_current_track(self):
        if not self.__hws: return
        return self._current_track
