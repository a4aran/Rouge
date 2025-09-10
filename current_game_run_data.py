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
                "shoot_on_death": [False,1,4]
            },
            {
                "shoot_on_death_up": 1
            }
        ]

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
                "blitz": [False,1,"damage",-0.25],
                "particle_accelerator": [False,0.01,"bullet_speed",-0.4]
            }
        self.active_upgrades[2]={
                "shoot_on_death": [False, 1, 4]
            }
        self.active_upgrades[3] = {
            "shoot_on_death_up": 1
        }

        self.heal_q = 0
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
        return int(b_spd * self.get_second_lvl("particle_accelerator")[1]) if self.get_second_lvl("particle_accelerator")[0] else 0

    def get_lvl_3_active_upgrades(self):
        temp = []
        for kind in self.active_upgrades[2]:
            temp_up = self.active_upgrades[2][kind]
            if temp_up[0] and (temp_up[1] != temp_up[2]):
                temp.append(kind)
        if not temp:
            temp = []
        return temp

    def chance_mult(self):
        m = 1
        if self.get_second_lvl("double_trouble")[0]:
            m *= 2
        return m

cur_run_data = RunManager()