from ar_math_helper import formulas

lvl1 = {
    "damage": 0,
    "pierce": 0,
    "bullet_speed": 0,
    "firerate": 0,
}
lvl2 = {
    "freezing_b": [False, 10, "firerate", -0.1],
    "triple_shot": [False, 0.10, "firerate", -0.1],
    "double_trouble": [False, -10],
    "bounce": [False, 0.2, "damage", -0.1],
    "blitz": [False, 3, "damage", -0.25],
    "particle_accelerator": [False, 0.01, "bullet_speed", -0.4],
    "homing_b": [True, 1, "bullet_speed", -0.2]
}
lvl3 = {
    "shoot_on_death": [False, 1, 4],
    "lifesteal": [False, 0.05, 0.25]
}

lvl4 = {
    "shoot_on_death_up": 1,
    "lifesteal_up": 0.05,
}

# -- Stats Provider -- #

lvl1_stats = {
    "damage": lambda data, wave, context, extra: [formulas.damage_upgrade(wave)],
    "pierce": lambda data, wave, context, extra: [1],
    "bullet_speed": lambda data, wave, context, extra: [formulas.b_speed_upgrade(wave)],
    "firerate": lambda data, wave, context, extra: [formulas.firerate_upgrade(wave)],
    "heal": lambda data, wave, contextm, extra: [data[0]]
}
lvl2_stats = {
    "freezing_b": lambda data, wave, context, extra: [data[1],round(data[3] * 100)],
    "triple_shot": lambda data, wave, context, extra: [
        round(data[1] * 100 * context["chance_mult"]),
        round(data[3] * 100)],
    "double_trouble": lambda data, wave, context, extra: [""],
    "bounce": lambda data, wave, context, extra: [
        round(data[1] * 100 * context["chance_mult"]),
        round(data[3] * 100)
        ],
    "blitz": lambda data, wave, context, extra: [
        round(data[1]),
        round(data[3] * 100)
    ],
    "particle_accelerator": lambda data, wave, context, extra: [
        data[1],
        round(data[3] * 100)
    ],
    "homing_b": lambda data, wave, context, extra: [
        data[1],
        round(data[3] * 100)
    ]
}
lvl3_stats = {
    "shoot_on_death": lambda data, wave, context, extra: [data[1],data[2]],
    "lifesteal":lambda data, wave, context, extra: [
        round(data[1] * 100 * context["chance_mult"]),
        context["lifesteal_amount"],
        round(data[2] * 100 * context["chance_mult"]),
    ],
}

lvl4_stats = {
        "shoot_on_death_up": lambda data, wave, context, extra: [
            data,
            extra[2]["shoot_on_death"][1],
            extra[2]["shoot_on_death"][2],
        ],
        "lifesteal_up": lambda data, wave, context, extra: [
            round(data * 100),
            round(extra[2]["lifesteal"][1] * context["chance_mult"] * 100),
            round(extra[2]["lifesteal"][2] * context["chance_mult"] * 100),
        ],
}


