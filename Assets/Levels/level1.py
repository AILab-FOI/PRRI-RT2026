"""
Level 1 configuration
"""
from Assets.Levels.base_level import create_base_level_structure
from Assets.npcs.enemy_npcs import StakorNPC, KlonoviNPC

def get_level_data():
    """Return the complete level 1 data"""
    level_data = create_base_level_structure()

    level_data['intro_dialogue'] = 'level1_intro'

    level_data['weapons'] = [
        {
            'position': (2.5, 3.5),
            'weapon_index': 0,
            'path': 'resources/sprites/weapon/pistol_stand.png'
        }
    ]

    level_data['enemies'] = {
        'count': 4,
        'types': [StakorNPC, KlonoviNPC],
        'weights': [70, 30],
        'restricted_area': {(i, j) for i in range(5) for j in range(7)},
        'fixed_positions': []
    }

    level_data['heal_item'] = [
        {'position': (2.5, 6.5)},
    ]

    level_data['ammo_pickup'] = [
        {'position': (6.5, 6.5)},
    ]

    return level_data
