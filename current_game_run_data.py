import ast
import random
from typing import TYPE_CHECKING
import upgrades_data as u_data
if TYPE_CHECKING:
    from c_objects.world import World

class RunManager:
    def __init__(self):
        self.active_upgrades = [
            u_data.lvl1.copy(),
            u_data.lvl2.copy(),
            u_data.lvl3.copy(),
            u_data.lvl4.copy()
        ]

        self.lifesteal_amount = 1
        self.heal_q = 0
        self.last_max_health_upgrade_wave = 0
        self.add_max_hp = 0

        self.selected_character = 0

        self.request_player_upgrade = False

        self.should_load_save = False

        self.stats = [
            u_data.lvl1_stats.copy(),
            u_data.lvl2_stats.copy(),
            u_data.lvl3_stats.copy(),
            u_data.lvl4_stats.copy()
        ]

    def round_active_upgrades(self):
        level = self.active_upgrades[0]
        for kind in level:
            if kind == "firerate":
                level[kind] = round(level[kind], 2)
            elif not isinstance(level[kind], int):
                level[kind] = round(level[kind])


    def reset(self):
        self.active_upgrades = [
            u_data.lvl1.copy(),
            u_data.lvl2.copy(),
            u_data.lvl3.copy(),
            u_data.lvl4.copy()
        ]

        self.heal_q = 0
        self.lifesteal_amount = 1
        self.last_max_health_upgrade_wave = 0
        self.add_max_hp = 0
        self.request_player_upgrade = False
        self.selected_character = 0

    def get_second_lvl(self,name: str) -> list:
        return self.active_upgrades[1][name]

    def get_random_chance(self,chance: float):
        if self.get_second_lvl("double_trouble")[0]:
            chance *= 2
        return random.random() <= chance

    def get_blitz_additional_dmg(self,firerate:float):
        return int(int(firerate) * self.get_second_lvl("blitz")[1]) if self.get_second_lvl("blitz")[0] else 0

    def get_PA_additional_fr(self,b_spd:float):
        return round(b_spd * self.get_second_lvl("particle_accelerator")[1],2) if self.get_second_lvl("particle_accelerator")[0] else 0

    def get_lvl_3_active_upgrades(self):
        temp = []
        for kind in self.active_upgrades[2]:
            temp_up = self.active_upgrades[2][kind]
            if temp_up[0] and (temp_up[1] < temp_up[2]):
                temp.append(kind)
        if not temp:
            temp = []
        return temp

    def chance_mult(self):
        m = 1
        if self.get_second_lvl("double_trouble")[0]:
            m *= 2
        return m

    def get_context(self):
        ctx = {}
        for lvl in self.active_upgrades:
            for k, v in lvl.items():
                ctx[k] = v
        ctx["chance_mult"] = self.chance_mult()
        ctx["lifesteal_amount"] = self.lifesteal_amount
        return ctx

    def load_save(self,save_data):
        if save_data == "":
            self.reset()
        else:
            self.active_upgrades = ast.literal_eval(save_data)
        self.request_player_upgrade = True

cur_run_data = RunManager()


class SaveManager:
    def __init__(self):
        self.version = 3
        self.coder = self._Coder()
        self.upgrade_save_data_decoded_str = str(cur_run_data.active_upgrades)
        self.upgrade_save_data_encoded = self.coder.encode(self.upgrade_save_data_decoded_str)

        self.upgrade_file_save_encoded = self.read_from_upgrade_file()[0]
        self.upgrade_file_save_decoded = self.read_from_upgrade_file()[1]

        self.other_save_data_decoded_str = ""
        self.other_save_data_encoded = ""

        self.other_file_save_encoded = self.read_from_other_file()[0]
        self.other_file_save_decoded = self.read_from_other_file()[1]

        if self.other_file_save_decoded == "" or self.upgrade_file_save_decoded == "":
            self.other_file_save_decoded = ""
            self.upgrade_file_save_decoded = ""

    class _Coder:
        def __init__(self):
            plain = 'abcdefghijklmnopqrstuvwxyz0123456789[]{}":,.-_FT'
            cipher = '!@#$%^&*()~-_=+/QAZWSXEDCRFVTGBYHNUJMIK<OL>P:?{"}|.'

            self.dictionary = {p: c for p, c in zip(plain, cipher)}
            self.reverse_dictionary = {c: p for p, c in zip(plain, cipher)}

        def encode(self, text: str) -> str:
            return ''.join(self.dictionary.get(char, char) for char in text)

        def decode(self, text: str) -> str:
            return ''.join(self.reverse_dictionary.get(char, char) for char in text)

    def save_to_file(self):
        encoded_version = self.coder.encode(self.stringify_version())
        to_write = encoded_version + self.upgrade_save_data_encoded
        with open("save/upgrades.txt", "w", encoding="utf-8") as file:
            file.write(to_write)
        to_write = encoded_version + self.other_save_data_encoded
        with open("save/other.txt", "w", encoding="utf-8") as file:
            file.write(to_write)

    def read_from_upgrade_file(self):
        with open("save/upgrades.txt", "r", encoding="utf-8") as file:
            content_raw = file.read()
        content = self.coder.decode(content_raw)
        content = "" if not content[:5] == self.stringify_version() else content
        content = content[5:]
        return content_raw,content

    def read_from_other_file(self):
        with open("save/other.txt", "r", encoding="utf-8") as file:
            content_raw = file.read()
        content = self.coder.decode(content_raw)
        content = "" if not content[:5] == self.stringify_version() else content
        content = content[5:]
        return content_raw,content

    def create_other_save_dict(self,world: "World"):
        return {
            "player_health": world.player.health,
            "player_max_hp": world.player.max_health,
            "heal_q": cur_run_data.heal_q,
            "last_max_health_upgrade_wave": cur_run_data.last_max_health_upgrade_wave,
            "add_max_hp": cur_run_data.add_max_hp,
            "wave": world.wave_count,
            "selected_character": cur_run_data.selected_character
        }

    def stringify_version(self):
        return f"{self.version:04}v"

    def update(self,world: "World"):
        self.other_save_data_decoded_str = str(self.create_other_save_dict(world))
        self.other_save_data_encoded = self.coder.encode(self.other_save_data_decoded_str)

        self.upgrade_save_data_decoded_str = str(cur_run_data.active_upgrades)
        self.upgrade_save_data_encoded = self.coder.encode(self.upgrade_save_data_decoded_str)
        self.save_to_file()

    def reset(self):
        with open("save/upgrades.txt", "w", encoding="utf-8") as file:
            file.write("")
        with open("save/other.txt", "w", encoding="utf-8") as file:
            file.write("")
        self.upgrade_file_save_encoded = self.read_from_upgrade_file()[0]
        self.upgrade_file_save_decoded = self.read_from_upgrade_file()[1]
        self.other_file_save_encoded = self.read_from_other_file()[0]
        self.other_file_save_decoded = self.read_from_other_file()[1]


save_manager = SaveManager()
print(save_manager.coder.encode("0002v{'player_health': 100, 'player_max_hp': 100, 'heal_q': 0, 'last_max_health_upgrade_wave': 0, 'add_max_hp': 0, 'wave': 14, 'selected_character': 0}"))