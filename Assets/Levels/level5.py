"""
Level 5 configuration
"""
from Assets.npcs.enemy_npcs import BossNPC, KlonoviNPC
from Assets.Levels.base_level import create_base_level_structure


def get_level_data():
    """Return the complete level 5 data"""
    level_data = create_base_level_structure()

    level_data['doors'] = []

    level_data['weapons'] = [
        {
            'position': (16.5, 3.5),
            'weapon_index': 2,
            'path': 'resources/sprites/weapon/plasma_stand.png'
        }
    ]

    level_data['powerups'] = [
        {
            'position': (6, 11),
            'powerup_type': 'invulnerability'
        },
        {
            'position': (20, 22),
            'powerup_type': 'invulnerability'
        },
        {
            'position': (11, 6),
            'powerup_type': 'invulnerability'
        },
        {
            'position': (15, 6),
            'powerup_type': 'invulnerability'
        },
    ]

    level_data['sprites'] = []

    level_data['enemies'] = {
        'waves': [
            {
                'count': 5,
                'types': [KlonoviNPC],
                'weights': [100],
                'fixed_positions': [
                    {'type': BossNPC, 'position': (13, 17)},
                    {'type': KlonoviNPC, 'position': (11, 15)},
                    {'type': KlonoviNPC, 'position': (15, 15)},
                ],
                'max_enemies_on_map': 5
            }
        ],
        'restricted_area': {(i, j) for i in range(10, 17) for j in range(6)},
        'wave_delay': 3000
    }

    level_data['dialogue_npcs'] = [
        {
            'pos': (13.5, 22.5),
            'dialogue_id': 'marvin_ending',
            'path': 'resources/sprites/npc/dialogue_npc/0.png'
        }
    ]

    return level_data