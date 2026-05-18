"""
Level 2 configuration
"""
from Assets.npcs.enemy_npcs import StakorNPC, TosterNPC
from Assets.Levels.base_level import create_base_level_structure


def get_level_data():
    """Return the complete level 2 data"""
    level_data = create_base_level_structure()

    level_data['terminals'] = [
        {
            'position': (1, 17),
            'code': '8332',
            'unlocks_door_id': None
        }
    ]

    level_data['doors'] = []

    level_data['weapons'] = [
        {
            'position': (2.5, 5),
            'weapon_index': 1,
            'path': 'resources/sprites/weapon/puska_stand.png'
        },
    ]
    level_data['powerups'] = []

    level_data['sprites'] = []

    level_data['enemies'] = {
        'waves': [
            {
                'count': 15,
                'types': [StakorNPC, TosterNPC],
                'weights': [60, 40],
                'fixed_positions': [],
                'max_enemies_on_map': 15
            }
        ],
        'restricted_area': {(i, j) for i in range(10) for j in range(10)},
        'wave_delay': 3000
    }

    

    level_data['heal_item'] = [
        {'position': (5.5, 5.5)},
        {'position': (5.5, 1.5)},
        {'position': (8.5, 3.5)},
    ]

    level_data['ammo_pickup'] = [
        {'position': (5.5, 2.5)}
    ]

    return level_data