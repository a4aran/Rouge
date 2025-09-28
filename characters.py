characters =[
    {
        "name": "player0",
        "ability":{
            "type": "activated",
            "name": "dash",
            "cooldown": [0,3,True],
            "active": [0,0.5,False],
        },
        "base_stats":{
            "speed": 120,
            "firerate": 1,
            "max_hp": 100,
            "attack_dmg": 10,
            "pierce": 1,
            "b_speed": 170,
            "armor": 0
        },
        "upgradable_stats": "pierce"
    },
    {
        "name": "shocker",
        "ability": {
            "type": "activated",
            "name": "shockwave",
            "cooldown": [0, 0.9, True],
            "one_shot": True,
        },
        "base_stats": {
            "speed": 160,
            "firerate": 0.5,
            "max_hp": 200,
            "attack_dmg": 10,
            "pierce": 1,
            "b_speed": 100,
            "armor": 4
        },
        "upgradable_stat": "armor"
    }
]
