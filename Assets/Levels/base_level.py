"""
Base level module providing the common structure for all game levels
"""

def create_base_level_structure():
    """Returns a dictionary with the standard structure for all game levels"""
    return {
        'terminals': [],
        'doors': [],
        'weapons': [],
        'powerups': [],
        'sprites': [],
        'dialogue_npcs': [],
        'enemies': {
            'count': 0,
            'types': [],
            'weights': [],
            'restricted_area': set(),
            'fixed_positions': []
        }
    }
