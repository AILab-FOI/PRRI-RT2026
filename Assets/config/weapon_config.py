PISTOL_CONFIG = {
    'name': 'pistol',
    'path': 'resources/sprites/weapon/pistol/0.png',
    'scale': 0.22,
    'animation_time': 210,
    'fire_cooldown': 420,
    'damage': 25,
    'magSize': 7, #ammo in weapon
    'bagSize': 21, #ammon in the reload pool
    'accuracy': 0.95,
    'auto_fire': False,
    'sound': 'pistolj',
    'reload_sound': 'reload_pistolj',
    'description': 'Standard issue sidearm. Reliable and accurate.'
}

SMG_CONFIG = {
    'name': 'smg',
    'path': 'resources/sprites/weapon/smg/0.png',
    'scale': 0.4,
    'animation_time': 70,
    'fire_cooldown': 120,
    'max_range': 4,
    'damage': 15,
    'magSize': 30, #ammo in weapon
    'bagSize': 300, #ammon in the reload pool
    'accuracy': 0.75,
    'auto_fire': True,
    'auto_fire_delay': 70,
    'reload_sound': 'reload_smg',
    'reload_duration': 700,
    'sound': 'smg',
    'right_offset': 0,
    'description': 'Rapid-fire weapon ideal for close quarters combat.'
}

PLASMA_GUN_CONFIG = {
    'name': 'plasmagun',
    'path': 'resources/sprites/weapon/plasmaGun/0.png',
    'scale': 0.5,
    'animation_time': 500,
    'fire_cooldown': 650,
    'damage': 50,
    'magSize': 7, #ammo in weapon
    'bagSize': 21, #ammon in the reload pool
    'accuracy': 0.9,
    'auto_fire': False,
    'sound': 'plasmagun',
    'right_offset': 200,
    'description': 'Advanced plasma weapon with devastating firepower.'
}

BAT_CONFIG = {
    'name': 'bat',
    'path': 'resources/sprites/weapon/bat/0.png',
    'scale': 0.45,
    'animation_time': 120,
    'fire_cooldown': 400,       
    'damage': 9999,             
    'magSize': 1,               
    'bagSize': 0,
    'accuracy': 1.0,
    'auto_fire': False,
    'bat_range': 3,           
    'max_uses': 4,              
    'max_targets': 3,           
    'sound': 'bat_swing',       
    'description': 'A trusty bat. Four swings, then it breaks.',
}


WEAPON_CONFIGS = {
    'pistol': PISTOL_CONFIG,
    'smg': SMG_CONFIG,
    'plasmagun': PLASMA_GUN_CONFIG,
    'bat': BAT_CONFIG
}

def get_weapon_config(weapon_name):
    return WEAPON_CONFIGS.get(weapon_name.lower())
