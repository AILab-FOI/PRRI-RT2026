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
                'count': 0, # Privremeno isključeno zbog testiranja tekstura
                'types': [KlonoviNPC],
                'weights': [100],
                'fixed_positions': []
            },
            {
                # Wave 2
                'count': 0,
                'types': [KlonoviNPC, JazavacNPC],
                'weights': [70, 30],
                'fixed_positions': []
            },
            {
                # Wave 3
                'count': 0,
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
    ]
    #{'position': (11.5, 11.5), 'powerup_type': 'invulnerability'}, ovo se stoposto ispise
    level_data['dialogue_npcs'] = [
       {
            'pos': (30.8, 12.3),
            'dialogue_id': 'level2_puzzle',
            'path': 'resources/sprites/npc/dialogue_npc/0.png'
       }
    ]

    level_data['pickup_item'] = [
        {'position':(11.5, 11.5)}
    ]

    return level_data
