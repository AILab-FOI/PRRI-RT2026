"""
Level 6 configuration
"""
from Assets.npcs.enemy_npcs import BossNPC
from Assets.Levels.base_level import create_base_level_structure

def get_level_data():
    """Return the complete level 6 data"""
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

    # Decorative sprites - unique to level 4
    level_data['sprites'] = [

    ]

    # Enemy configuration
    level_data['enemies'] = {
        'count': 0,
        'types': [],
        'weights': [],
        'restricted_area': {(i, j) for i in range(9, 12) for j in range(9, 12)},
        'fixed_positions': []
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
