"""
Level 3 configuration
"""
from Assets.npcs.enemy_npcs import KlonoviNPC, JazavacNPC
from Assets.Levels.base_level import create_base_level_structure

def get_level_data():
    """Return the complete level 3 data"""
    level_data = create_base_level_structure()

    level_data['enemies'] = {
        'waves': [
            {
                # Wave 1
                'count': 10,
                'types': [KlonoviNPC],
                'weights': [100],
                'fixed_positions': []
            },
            {
                # Wave 2
                'count': 12,
                'types': [KlonoviNPC, JazavacNPC],
                'weights': [70, 30],
                'fixed_positions': []
            },
            {
                # Wave 3
                'count': 8,
                'types': [JazavacNPC],
                'weights': [100],
                'fixed_positions': []
            }
        ],
        'restricted_area': {(i, j) for i in range(5) for j in range(5)}
    }

    level_data['powerups'] = [
        {'position': (15.5, 15.5), 'powerup_type': 'invulnerability'},
        {'position': (10.5, 10.5), 'powerup_type': 'invulnerability'},
        {'position': (20.5, 10.5), 'powerup_type': 'invulnerability'},
    ]

    level_data['dialogue_npcs'] = [
       {
            'pos': (30.8, 12.3),
            'dialogue_id': 'level2_puzzle',
            'path': 'resources/sprites/npc/dialogue_npc/0.png'
       }
    ]

    return level_data
