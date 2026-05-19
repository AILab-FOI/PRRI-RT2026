"""
Level 4 configuration
"""
from Assets.npcs.enemy_npcs import MadracNPC, ParazitNPC, TosterNPC
from Assets.Levels.base_level import create_base_level_structure

def get_level_data():
    """Return the complete level 4 data"""
    level_data = create_base_level_structure()

    level_data['powerups'] = [
        {
            'position': (17.5, 1.5),
            'powerup_type': 'invulnerability'
        },
        {
            'position': (17.5, 17.5),
            'powerup_type': 'invulnerability'
        },
    ]

    # Doors
    level_data['doors'] = [
        {'position': (3, 4), 'door_id': 1, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (5, 6), 'door_id': 2, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (13, 6), 'door_id': 3, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (15, 6), 'door_id': 4, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (3, 8), 'door_id': 5, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (7, 8), 'door_id': 6, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (11, 8), 'door_id': 7, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (5, 10), 'door_id': 8, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (9, 10), 'door_id': 9, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (3, 12), 'door_id': 10, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (7, 12), 'door_id': 11, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (5, 14), 'door_id': 12, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (7, 14), 'door_id': 13, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (3, 16), 'door_id': 14, 'requires_code': False, 'code': None, 'requires_door_id': None},
    ]

    # Pickup items (collectible counters)
    level_data['pickup_item'] = [
        {'position': (1.5, 2.5)},
        {'position': (3.5, 3.5)},
        {'position': (9.5, 4.5)},
        {'position': (14.5, 3.5)},
        {'position': (1.5, 12.5)},
    ]

    # Decorative sprites
    level_data['sprites'] = [

    ]

    # Enemy configuration
    level_data['enemies'] = {
        'count': 8,
        'types': [ParazitNPC, MadracNPC],
        'weights': [30, 70],
        'restricted_area': {
            *{(i, j) for i in range(5) for j in range(5)}
            },
        'fixed_positions': [
            {'type': ParazitNPC, 'position': (1.5, 13.5)},
            {'type': ParazitNPC, 'position': (17.5, 17.5)},
        ]
    }

    return level_data
