"""
Level 5 configuration
"""
from Assets.npcs.enemy_npcs import BossNPC, KlonoviNPC, StakorNPC, TosterNPC, ParazitNPC, JazavacNPC, MadracNPC
from Assets.Levels.base_level import create_base_level_structure

def get_level_data():
    """Return the complete level 5 data"""
    level_data = create_base_level_structure()

    level_data['doors'] = []

    level_data['weapons'] = []

    level_data['powerups'] = [
        {'position': (2.5, 13.5), 'powerup_type': 'invulnerability'},
        {'position': (18.5, 13.5), 'powerup_type': 'invulnerability'},
        {'position': (5.5, 15.5), 'powerup_type': 'invulnerability'},
        {'position': (15.5, 15.5), 'powerup_type': 'invulnerability'},
        {'position': (9.5, 7.5), 'powerup_type': 'invulnerability'},
        {'position': (11.5, 7.5), 'powerup_type': 'invulnerability'},
    ]

    # Decorative sprites - unique to level 6
    level_data['sprites'] = []

    # Enemy configuration
    level_data['enemies'] = {
        'waves': [
            {
                'count': 1,
                'types': [BossNPC],
                'weights': [100],
                'fixed_positions': [
                    {'type': BossNPC, 'position': (15, 15)},
                ],
                'max_enemies_on_map': 1
            }
        ],
        'restricted_area': {
            (i, j) for i in range(7, 12) for j in range(7, 12)
        } | {
            (i, j) for i in range(7, 12) for j in range(13, 19)
        },
        'wave_delay': 3000
    }

    # Dialogue NPCs
    level_data['dialogue_npcs'] = [
        {
            'pos': (13.5, 30.5),
            'dialogue_id': 'marvin_ending',
            'path': 'resources/sprites/npc/dialogue_npc/0.png'
        }
    ]

    return level_data
