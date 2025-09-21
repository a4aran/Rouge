import matplotlib.pyplot as plt

import ar_math_helper
from ar_math_helper import formulas

def difficulty_curve(waves:int,runs_to_avg:int):
    b_spd_list = []
    firerate_list = []
    damage_list = []
    enemy_scaling_list = []
    boss_scaling_list = []

    # - Bullet Speed -#
    temp_to_avg = []
    for run in range(runs_to_avg):
        temp = []
        for wave in range(waves):
            temp.append(formulas.b_speed_upgrade(wave))
        temp_to_avg.append(temp)
    for wave in range(waves):
        total = 0
        for data in temp_to_avg:
            total += data[wave]
        total /= runs_to_avg
        b_spd_list.append(total)


    # - Firerate -#
    temp_to_avg = []
    for run in range(runs_to_avg):
        temp = []
        for wave in range(waves):
            temp.append(formulas.firerate_upgrade(wave))
        temp_to_avg.append(temp)
    for wave in range(waves):
        total = 0
        for data in temp_to_avg:
            total += data[wave]
        total /= runs_to_avg
        firerate_list.append(total)

    # - Damage -#
    temp_to_avg = []
    for run in range(runs_to_avg):
        temp = []
        for wave in range(waves):
            temp.append(formulas.damage_upgrade(wave))
        temp_to_avg.append(temp)
    for wave in range(waves):
        total = 0
        for data in temp_to_avg:
            total += data[wave]
        total /= runs_to_avg
        damage_list.append(total)

    # - Enemy Scaling - #
    for wave in range(waves):
        enemy_scaling_list.append(formulas.enemy_scaling(wave))

    # - Boss Scaling - #
    for wave in range(waves):
        boss_scaling_list.append(formulas.boss_hp_mult(wave))

    # ! Difficulty Curve Calculation ! #
    difficulty_curve_list = []
    for wave in range(waves):
        temp = 0
        temp += b_spd_list[wave] * -0.15
        temp += firerate_list[wave] * -0.65
        temp += damage_list[wave] * -0.65
        temp += enemy_scaling_list[wave]*0.8 * (ar_math_helper.formulas.enemy_count(wave) * 0.1)
        temp += boss_scaling_list[wave] *0.5
        difficulty_curve_list.append(temp)
    return difficulty_curve_list

w = int(input("Number of waves: "))
ar = int(input("Number of runs to avg: "))
waves = [wave for wave in range(w)]
plt.plot(waves,difficulty_curve(w,ar),linewidth = 2)
plt.suptitle("Difficulty Curve")
plt.xlabel("Waves")
plt.ylabel("Difficulty")
plt.show()
