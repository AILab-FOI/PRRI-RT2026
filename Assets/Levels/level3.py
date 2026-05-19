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
                'count': 10,
                'types': [KlonoviNPC],
                'weights': [100],
                'fixed_positions': [],
                'max_enemies_on_map': 5
            },
            {
                'count': 13,
                'types': [KlonoviNPC, JazavacNPC],
                'weights': [70, 30],
                'fixed_positions': [],
                'max_enemies_on_map': 10
            },
            {
                'count': 15,
                'types': [JazavacNPC],
                'weights': [100],
                'fixed_positions': [],
                'max_enemies_on_map': 10
            }
        ],
        'restricted_area': {(i, j) for i in range(5) for j in range(5)},
        'wave_delay': 3000
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
        {
            'position': (11.5, 11.5),
            'message': (
                "LOG ENTRY - Day 3: The rats have learned to operate the ship's"
                " intercom. They keep broadcasting elevator music into my cabin."
                " I've tried reasoning with them. They don't negotiate."
            )
        }
    ]

    return level_data