import ast
import copy
import random
from typing import TYPE_CHECKING

import characters
import upgrades_data as u_data
if TYPE_CHECKING:
    from c_objects.world import World

class RunManager:
    def __init__(self):
        self.active_stats = self.create_stats_dict()

        self.lifesteal_amount = 1
        self.shockwave_dmg_mult = 1
        self.heal_q = 0
        self.last_max_health_upgrade_wave = 0
        self.add_max_hp = 0

        self.selected_character = 1

        self.request_player_upgrade = False

        self.should_load_save = False

        self.stats = [
            u_data.lvl1_stats.copy(),
            u_data.lvl2_stats.copy(),
            u_data.lvl3_stats.copy(),
            u_data.lvl4_stats.copy()
        ]

    def round_active_upgrades(self):
        level = self.active_stats[0]
        for kind in level:
            if kind == "firerate":
                level[kind] = round(level[kind], 2)
            elif not isinstance(level[kind], int):
                level[kind] = round(level[kind])


    def reset(self):
        self.active_stats = self.create_stats_dict()
        self.heal_q = 0
        self.lifesteal_amount = 1
        self.last_max_health_upgrade_wave = 0
        self.add_max_hp = 0
        self.request_player_upgrade = False
        self.selected_character = 0

    def get_second_lvl(self,name: str) -> list:
        return self.active_stats[1][name]

    def get_random_chance(self,chance: float):
        if self.get_second_lvl("double_trouble"):
            chance *= 2
        return random.random() <= chance

    def get_blitz_additional_dmg(self,firerate:float):
        return int(int(firerate) * u_data.lvl2["blitz"][1]) if self.get_second_lvl("blitz") else 0

    def get_PA_additional_fr(self,b_spd:float):
        return round(b_spd * u_data.lvl2["particle_accelerator"][1],2) if self.get_second_lvl("particle_accelerator") else 0

    def get_lvl_3_active_upgrades(self):
        temp = []
        for kind in u_data.lvl3:
            temp_bool = self.active_stats[2][kind + "_bool"]
            temp_val = self.active_stats[2][kind + "_value"]
            if temp_bool and (temp_val < u_data.lvl3[kind][2]):
                temp.append(kind)
        if not temp:
            temp = []
        return temp

    def chance_mult(self):
        m = 1
        if self.get_second_lvl("double_trouble"):
            m *= 2
        return m

    def get_context(self):
        ctx = {}
        for lvl in self.active_stats:
            for k, v in lvl.items():
                ctx[k] = v
        ctx["chance_mult"] = self.chance_mult()
        ctx["lifesteal_amount"] = self.lifesteal_amount
        ctx["character_name"] = characters.characters[self.selected_character]["name"]
        ctx["lifesteal_upgrade_value"] = self.active_stats[2]["lifesteal_value"]
        ctx["shoot_on_death_value"] = self.active_stats[2]["shoot_on_death_value"]
        return ctx

    def load_save(self,save_data):
        if save_data is None:
            self.reset()
        else:
            self.active_stats = save_data["stats"]
            data = save_data["other"]
            self.heal_q = data["heal_q"]
            self.last_max_health_upgrade_wave = data["last_max_health_upgrade_wave"]
            self.add_max_hp = data["add_max_hp"]
            self.selected_character = data["selected_character"]
        self.request_player_upgrade = True

    def create_stats_dict(self):
        temp = [
            u_data.lvl1.copy(),
            copy.deepcopy(u_data.lvl2),
            copy.deepcopy(u_data.lvl3),
            u_data.lvl4.copy(),
        ]
        stats_dict =[
            {},
            {},
            {},
        ]

        for stat in temp[0]:
            stats_dict[0][stat] = 0
        for stat in temp[1]:
            stats_dict[1][stat] = False
        for stat in temp[2]:
            stats_dict[2][stat + "_bool"] = False
            stats_dict[2][stat + "_value"] = u_data.lvl3[stat][1]

        return stats_dict

cur_run_data = RunManager()


class SaveManager:
    def __init__(self):
        self.version = 4
        self.coder = self._Coder()
        self.loaded_save_file = self.load_and_decode()

    class _Coder:
        def __init__(self):
            plain = 'abcdefghijklmnopqrstuvwxyz0123456789[]{}":,.-_FT'
            cipher = '!@#$%^&*()~-_=+/QAZWSXEDCRFVTGBYHNUJMIK<OL>P:?{"}|'

            self.dictionary = {p: c for p, c in zip(plain, cipher)}
            self.reverse_dictionary = {c: p for p, c in zip(plain, cipher)}

        def encode(self, text: str) -> str:
            return ''.join(self.dictionary.get(char, char) for char in text)

        def decode(self, text: str) -> str:
            return ''.join(self.reverse_dictionary.get(char, char) for char in text)

    def encoded_string_version(self):
        return self.coder.encode("v" + f"{self.version:04d}")

    def write_save_file(self,world):
        file = {
            "stats": cur_run_data.active_stats,
            "other": {
                "player_health": world.player.health,
                "heal_q": cur_run_data.heal_q,
                "last_max_health_upgrade_wave": cur_run_data.last_max_health_upgrade_wave,
                "add_max_hp": cur_run_data.add_max_hp,
                "wave": world.wave_count,
                "selected_character": cur_run_data.selected_character
            }
        }
        print(str(file))
        file = self.encoded_string_version() + self.coder.encode(str(file))
        with open("./save/file.txt", "w", encoding="utf-8") as f:
            f.write(file)

    def load_and_decode(self):
        data = ""
        with open("./save/file.txt", "r", encoding="utf-8") as f:
            data = f.read()
        version = self.encoded_string_version()
        count = len(version)
        s = data[:count]
        print(self.coder.decode(data) + "loaded")
        return ast.literal_eval(self.coder.decode(data[count:])) if s == version else None

    def clear_save(self):
        with open("./save/file.txt", "w", encoding="utf-8") as f:
            f.write("clear")

save_manager = SaveManager()