"""
Level 4 configuration: The Keycard Hunt
"""
from Assets.npcs.enemy_npcs import MadracNPC, ParazitNPC, TosterNPC, KlonoviNPC
from Assets.Levels.base_level import create_base_level_structure


def get_level_data():
    """Return the complete level 4 data"""
    level_data = create_base_level_structure()

    level_data['player_spawn'] = (9.5, 18.5)

    level_data['terminals'] = [
        {'position': (3, 17), 'code': '1234', 'unlocks_door_id': None},
        {'position': (15, 17), 'code': '8888', 'unlocks_door_id': None},
        {'position': (3, 9), 'code': '7777', 'unlocks_door_id': None},
        {'position': (15, 3), 'code': '4040', 'unlocks_door_id': None},
    ]

    level_data['powerups'] = [
        {'position': (3.5, 3.5), 'powerup_type': 'invulnerability'},
    ]

    level_data['doors'] = [
        {'position': (9, 12), 'door_id': 1, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (6, 15), 'door_id': 2, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (12, 15), 'door_id': 3, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (6, 9), 'door_id': 4, 'requires_code': True, 'code': '1234', 'requires_door_id': None},
        {'position': (9, 6), 'door_id': 5, 'requires_code': True, 'code': '8888', 'requires_door_id': None},
        {'position': (12, 9), 'door_id': 6, 'requires_code': True, 'code': '4040', 'requires_door_id': None},
        {'position': (3, 6), 'door_id': 7, 'requires_code': False, 'code': None, 'requires_door_id': None},
        {'position': (12, 3), 'door_id': 8, 'requires_code': True, 'code': '7777', 'requires_door_id': None},
    ]

    level_data['heal_item'] = [
        {'position': (2.5, 3.5)},
        {'position': (4.5, 3.5)},
    ]

    level_data['ammo_pickup'] = [
        {'position': (3.5, 2.5)},
        {'position': (3.5, 4.5)},
        {'position': (9.5, 15.5)},
    ]

    level_data['pickup_item'] = [
        {
            'position': (1.5, 2.5),
            'message': (
                "A data pad left by the previous captain: 'Note to self —"
                " the answer may be 42, but the question is clearly \"How many"
                " rats can fit in one air duct?\" The answer: all of them.'"
            )
        },
        {
            'position': (3.5, 3.5),
            'message': (
                "E.D.D.I.E's latest system report: 'I have identified the"
                " intruders. They are rats. Big ones. Some are wearing"
                " improvised armor. Recommendation: don't panic. Actually,"
                " panic. It'll make the footage more entertaining.'"
            )
        },
        {
            'position': (9.5, 4.5),
            'message': (
                "Ship log — Day 12: The rats have unionized. Their demands"
                " include a dedicated cheese wing and a daily five-minute"
                " break from being vermin. Negotiations have broken down."
            )
        },
        {
            'position': (14.5, 3.5),
            'message': (
                "A page from the onboard survival guide: 'Rule #1: Always"
                " carry a towel. Rule #2: Never trust a rat in a waistcoat."
                " Rule #3: If you hear strange noises in the vents, pretend"
                " you didn't. It's easier that way.'"
            )
        },
        {
            'position': (1.5, 12.5),
            'message': (
                "A hastily scribbled note on the wall: 'If you're reading"
                " this, grab a towel, a weapon, and a sense of humor. The"
                " first two will keep you alive. The third will make you"
                " wish they hadn't. — The last guy'"
            )
        },
    ]

    level_data['sprites'] = []

    level_data['enemies'] = {
        'waves': [
            {
                'count': 6,
                'types': [ParazitNPC, MadracNPC, KlonoviNPC],
                'weights': [40, 40, 20],
                'fixed_positions': [
                    {'type': MadracNPC, 'position': (3, 15)},
                    {'type': ParazitNPC, 'position': (15, 15)},
                    {'type': TosterNPC, 'position': (3, 7)},
                    {'type': MadracNPC, 'position': (15, 5)},
                    {'type': ParazitNPC, 'position': (2, 2)},
                    {'type': MadracNPC, 'position': (4, 2)},
                    {'type': KlonoviNPC, 'position': (2, 4)},
                    {'type': MadracNPC, 'position': (4, 4)},
                ],
                'max_enemies_on_map': 10
            }
        ],
        'restricted_area': {
            (i, j) for i in range(7, 12) for j in range(7, 12)
        } | {
            (i, j) for i in range(7, 12) for j in range(13, 19)
        },
        'wave_delay': 3000
    }

    return level_data