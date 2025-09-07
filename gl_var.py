import window_size

window_center = (window_size.width/2,window_size.height/2)
btn_size = (240,80)

entities_id_counter = 0

status_effect = {
    "time":{
        "freeze": [0,0,False]
    }
}

level_1_upgrade_list = ["damage","pierce","bullet_speed","firerate"]
level_2_upgrade_list = ["freezing_b","triple_shot","double_trouble","bounce"]
