"""
Level 2 configuration
"""
from Assets.npcs.enemy_npcs import StakorNPC
from Assets.Levels.base_level import create_base_level_structure

def get_level_data():
    """Return the complete level 2 data"""
    level_data = create_base_level_structure()

    level_data['terminals'] = [
        {
            'position': (2, 14),
            'code': '8332',
            'unlocks_door_id': None
        }
    ]

    level_data['doors'] = [
        {
            'position': (15, 9),
            'door_id': 1,
            'requires_code': True,
            'code': '8332'
        },
        {
            'position': (15, 24),
            'door_id': 2,
            'requires_code': True,
            'code': '8332',
            'requires_door_id': 1
        }
    ]

    level_data['weapons'] = [
        {
            'position': (3, 1),
            'weapon_index': 1,
            'path': 'resources/sprites/weapon/puska_stand.png'
        },

    ]
    level_data['powerups'] = []

    level_data['sprites'] = [
        (('level2', 'ukras2'), (12.9, 33.5)),
        (('level2', 'ukras2'), (12.1, 33.5)),
        ('ukras2', (1.9, 26.1)),
        ('ukras2', (2.3, 26.1)),
        ('ukras2', (1.1, 26.5)),
        ('ukras2', (1.1, 27.0)),
        ('ukras2', (1.1, 27.5)),
        ('ukras1', (1.1, 28.0)),
        ('ukras1', (1.1, 28.5)),
        ('ukras1', (1.1, 29.0)),
        ('ukras2', (1.1, 29.5)),
        ('ukras2', (1.1, 30.0)),
        ('ukras2', (1.1, 30.5)),
        ('ukras2', (1.1, 31.0)),
        ('ukras2', (1.1, 31.5)),
        ('ukras1', (1.1, 32.0)),
        ('ukras1', (1.1, 32.5)),
        ('ukras1', (1.5, 32.9)),
        ('ukras1', (1.9, 32.9)),
        ('ukras1', (2.3, 32.9)),
        ('ukras2', (2, 27.0)),
        ('ukras2', (2, 27.5)),
        ('ukras1', (2, 28.0)),
        ('ukras1', (2, 28.5)),
        ('ukras1', (2, 29.0)),
        ('ukras2', (2, 29.5)),
        ('ukras2', (2, 30.0)),
        ('ukras2', (2, 30.5)),
        ('ukras2', (2, 31.0)),
        ('ukras2', (2, 31.5)),
        ('ukras1', (2, 32.0)),
        ('ukras2', (3, 27.0)),
        ('ukras2', (3, 27.5)),
        ('ukras1', (3, 28.0)),
        ('ukras1', (3, 28.5)),
        ('ukras1', (3, 29.0)),
        ('ukras2', (3, 29.5)),
        ('ukras2', (3, 30.0)),
        ('ukras2', (3, 30.5)),
        ('ukras2', (3, 31.0)),
        ('ukras2', (3, 31.5)),
        ('ukras1', (3, 32.0)),
        (('level2', 'ukras2'), (23.2, 33.5)),
        (('level2', 'ukras2'), (8.9, 33.8)),
        ('ukras1', (20.2, 12.2)),
        ('ukras2', (20.2, 12.7)),
        ('ukras1', (20.2, 13.2)),
        ('ukras2', (20.2, 13.7)),
        ('ukras1', (20.2, 14.2)),
        ('ukras2', (20.2, 14.7)),
        ('ukras1', (20.8, 12.7)),
        ('ukras1', (21.4, 12.7)),
        ('ukras2', (22, 12.7)),
        ('ukras1', (22.6, 12.7)),
        ('ukras2', (20.8, 13.7)),
        ('ukras1', (21.4, 13.7)),
        ('ukras2', (22, 13.7)),
        ('ukras2', (22.6, 13.7)),
        ('ukras2', (20.8, 14.7)),
        ('ukras1', (21.4, 14.7)),
        ('ukras2', (22, 14.7)),
        ('ukras1', (22.6, 14.7))
    ]

    level_data['enemies'] = {
        'count': 20,
        'types': [StakorNPC],
        'weights': [100],
        'restricted_area': {(i, j) for i in range(10) for j in range(10)},
        'fixed_positions': []
    }

    level_data['dialogue_npcs'] = [
        {
            'pos': (3.5, 2.5),
            'dialogue_id': 'marvin_intro',
            'path': 'resources/sprites/npc/dialogue_npc/0.png'
        }
    ]

    level_data['heal_item']=[#pozicija za heal item
        {'position': (5.5, 5.5)},
        {'position': (5.5, 1.5)},
        {'position': (8.5, 3.5)},
        ]

    level_data['ammo_pickup'] = [
        {'position':(5.5,2.5)}
    ]

    return level_data
