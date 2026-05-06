from Assets.Levels.base_level import create_base_level_structure
from Assets.scripts.MapGenerator.map_Generator import MapGenerator
from Assets.npcs.enemy_npcs import StakorNPC, KlonoviNPC

def build_runtime_level(seed):
    level_data = create_base_level_structure()

    generated = MapGenerator(seed).generate_map(width=20, height=19)

    level_data['map'] = generated['map']
    level_data['player_spawn'] = generated['player_spawn']
    level_data['rooms'] = generated['rooms']

    level_data['intro_dialogue'] = 'level1_intro'
    level_data['doors'] = []
    level_data['weapons'] = []
    level_data['enemies'] = {
        'count': 4,
        'types': [StakorNPC, KlonoviNPC],
        'weights': [70, 30],
        'restricted_area': set(),
        'fixed_positions': []
    }
    level_data['heal_item'] = []
    level_data['ammo_pickup'] = []

    return level_data