PISTOL_CONFIG = {
    'name': 'pistol',
    'path': 'resources/sprites/weapon/pistol/0.png',
    'scale': 0.22,
    'animation_time': 210,
    'damage': 25,
    'accuracy': 0.95,
    'auto_fire': False,
    'sound': 'pistolj',
    'description': 'Standard issue sidearm. Reliable and accurate.'
}

SMG_CONFIG = {
    'name': 'smg',
    'path': 'resources/sprites/weapon/smg/0.png',
    'scale': 1.2,
    'animation_time': 70,
    'damage': 15,
    'accuracy': 0.75,
    'auto_fire': True,
    'auto_fire_delay': 70,
    'sound': 'smg',
    'right_offset': 230,
    'description': 'Rapid-fire weapon ideal for close quarters combat.'
}

PLASMA_GUN_CONFIG = {
    'name': 'plasmagun',
    'path': 'resources/sprites/weapon/plasmagun/0.png',
    'scale': 0.5,
    'animation_time': 500,
    'damage': 50,
    'accuracy': 0.9,
    'auto_fire': False,
    'sound': 'plasmagun',
    'right_offset': 200,
    'description': 'Advanced plasma weapon with devastating firepower.'
}

WEAPON_CONFIGS = {
    'pistol': PISTOL_CONFIG,
    'smg': SMG_CONFIG,
    'plasmagun': PLASMA_GUN_CONFIG,
}

def get_weapon_config(weapon_name):
    return WEAPON_CONFIGS.get(weapon_name.lower())
