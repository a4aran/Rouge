import ast
import random


class RunManager:
    def __init__(self):
        self.active_upgrades = [
            {
                "damage": 0,
                "pierce": 0,
                "bullet_speed": 0,
                "firerate": 0,
            },
            {
                "freezing_b": [False, 10, "firerate", -0.1],
                "triple_shot": [False, 0.10, "firerate", -0.1],
                "double_trouble": [False, -10],
                "bounce": [False, 0.2, "damage", -0.1],
                "blitz": [False,2,"damage",-0.25],
                "particle_accelerator": [False,0.01,"bullet_speed",-0.3]
            },
            {
                "shoot_on_death": [False,1,4],
                "lifesteal": [False,0.05,0.25]
            },
            {
                "shoot_on_death_up": 1,
                "lifesteal_up": 0.05,
            }
        ]

        self.lifesteal_amount = 1
        self.heal_q = 0
        self.last_max_health_upgrade_wave = 0
        self.add_max_hp = 0

        self.request_player_upgrade = False

    def round_active_upgrades(self):
        level = self.active_upgrades[0]
        for kind in level:
            if kind == "firerate":
                level[kind] = round(level[kind], 2)
            elif not isinstance(level[kind], int):
                level[kind] = round(level[kind])


    def reset(self):
        level = self.active_upgrades[0]
        for kind in level:
            level[kind] = 0
        self.active_upgrades[1]=            {
                "freezing_b": [False, 10, "firerate", -0.1],
                "triple_shot": [False, 0.10, "firerate", -0.1],
                "double_trouble": [False, -10],
                "bounce": [False, 0.2, "damage", -0.1],
                "blitz": [False,3,"damage",-0.25],
                "particle_accelerator": [False,0.01,"bullet_speed",-0.4]
            }
        self.active_upgrades[2]={
                "shoot_on_death": [False,1,4],
                "lifesteal": [False,0.05,0.25]
            }
        self.active_upgrades[3] ={
                "shoot_on_death_up": 1,
                "lifesteal_up": 0.05,
            }

        self.heal_q = 0
        self.lifesteal_amount = 1
        self.last_max_health_upgrade_wave = 0
        self.add_max_hp = 0
        self.request_player_upgrade = False

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
    
    def load_save(self,save_data):
        if save_data == "":
            print("a")
            self.reset()
        else:
            self.active_upgrades = ast.literal_eval(save_data)
        self.request_player_upgrade = True
        print(self.active_upgrades)

cur_run_data = RunManager()


class SaveManager:
    def __init__(self):
        self.coder = self._Coder()
        self.upgrade_save_data_decoded_str = str(cur_run_data.active_upgrades)
        self.upgrade_save_data_encoded = self.coder.encode(self.upgrade_save_data_decoded_str)

        self.upgrades_file_save_encoded = self.read_from_file()
        self.upgrade_file_save_decoded = self.coder.decode(self.upgrades_file_save_encoded)

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
        with open("save/upgrades.txt", "w", encoding="utf-8") as file:
            file.write(self.upgrade_save_data_encoded)

    def read_from_file(self):
        with open("save/upgrades.txt", "r", encoding="utf-8") as file:
            content = file.read()
        return content

    def update(self):
        self.upgrade_save_data_decoded_str = str(cur_run_data.active_upgrades)
        self.upgrade_save_data_encoded = self.coder.encode(self.upgrade_save_data_decoded_str)
        print(self.upgrade_save_data_decoded_str)
        self.save_to_file()


save_manager = SaveManager()