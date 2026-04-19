"""
Level 1 configuration
"""
from Assets.Levels.base_level import create_base_level_structure


def get_level_data():
    """Return the complete level 1 data"""
    level_data = create_base_level_structure()

    level_data['weapons'] = [
        {
            'position': (10, 10),
            'weapon_index': 0,
            'path': 'resources/sprites/weapon/pistol_stand.png'
        }
    ]

    level_data['enemies'] = {
        'count': 0,
        'types': [],
        'weights': [],
        'restricted_area': {(i, j) for i in range(9, 12) for j in range(9, 12)},
        'fixed_positions': []
    }

    return level_data
