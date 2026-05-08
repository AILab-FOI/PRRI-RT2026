import math
from Assets import settings as s
from Assets.Levels.base_level import create_base_level_structure
from Assets.scripts.MapGenerator.map_Generator import MapGenerator
from Assets.npcs.enemy_npcs import StakorNPC, KlonoviNPC


def build_runtime_level(seed, level_id=99):
    level_data = create_base_level_structure()

    map_size = s.PROCEDURAL_MAP_SIZE.get(level_id, (30, 30))
    tile_set = s.PROCEDURAL_TILE_SET.get(level_id, {'wall': 9, 'exit': 30})
    wave_data = s.PROCEDURAL_WAVES.get(
        level_id,
        {
            'start_enemies': 5,
            'types': ['StakorNPC'],
            'weights': [100],
            'safe_spawn_radius': 12
        }
    )
    spawn_counts = s.PROCEDURAL_ITEMS.get(level_id, {'weapons': 1, 'heals': 2, 'ammo': 2})
    room_settings = s.PROCEDURAL_ROOM_SETTINGS.get(
        level_id,
        {
            'size_multiplier': 1.0,
            'room_count': 7,
            'corridor_thickness': 1,
            'force_spawn_room': True,
            'spawn_room_size': (7, 7)
        }
    )

    enemy_classes = {'StakorNPC': StakorNPC, 'KlonoviNPC': KlonoviNPC}
    selected_enemy_types = [enemy_classes[t] for t in wave_data['types']]

    generator = MapGenerator(seed, wall_id=tile_set['wall'], exit_id=tile_set['exit'])
    
    generated = generator.generate_map(
    width=map_size[0],
    height=map_size[1],
    room_size_multiplier=room_settings.get('size_multiplier', 1.0),
    room_count=room_settings.get('room_count', 7),
    corridor_thickness=room_settings.get('corridor_thickness', 1),
    force_spawn_room=room_settings.get('force_spawn_room', True)
)

    level_data['map'] = generated['map']
    level_data['player_spawn'] = generated['player_spawn']
    level_data['rooms'] = generated['rooms']

    px, py = level_data['player_spawn']
    safe_radius = wave_data.get('safe_spawn_radius', 12)
    restricted_area = set()

    for y in range(map_size[1]):
        for x in range(map_size[0]):
            dist = math.hypot((x + 0.5) - px, (y + 0.5) - py)
            if dist <= safe_radius:
                restricted_area.add((x, y))

    occupied = [level_data['player_spawn']]

    # Pistol 2 tiles in front of player
    player_angle = getattr(s, 'PLAYER_ANGLE', 0)
    pistol_pos = generator.pick_position_in_front_of_player(
        generated['map'],
        level_data['player_spawn'],
        player_angle,
        distance_tiles=2
    )

    formatted_weapons = []
    if pistol_pos is not None:
        formatted_weapons.append({
            'weapon_index': 0,   # pistol
            'path': 'resources/sprites/weapon/pistol/0.png',
            'position': pistol_pos
        })
        occupied.append(pistol_pos)

    # Optional extra random weapons from settings
    extra_weapon_count = max(0, spawn_counts.get('weapons', 0) - len(formatted_weapons))
    weapon_pos = generator.pick_random_locations(generated['map'], extra_weapon_count, occupied)
    occupied.extend(weapon_pos)

    for pos in weapon_pos:
        formatted_weapons.append({
            'weapon_index': 1,
            'path': 'resources/sprites/weapon/shotgun/0.png',
            'position': pos
        })

    heal_pos = generator.pick_random_locations(generated['map'], spawn_counts['heals'], occupied)
    occupied.extend(heal_pos)

    ammo_pos = generator.pick_random_locations(generated['map'], spawn_counts['ammo'], occupied)
    occupied.extend(ammo_pos)

    formatted_heals = [{'position': pos} for pos in heal_pos]
    formatted_ammo = [{'position': pos} for pos in ammo_pos]

    level_data['intro_dialogue'] = 'level99_intro'
    level_data['terminals'] = []
    level_data['doors'] = []
    level_data['weapons'] = formatted_weapons
    level_data['heal_item'] = formatted_heals
    level_data['ammo_pickup'] = formatted_ammo

    level_data['wave_system'] = {
        'total_waves': wave_data.get('total_waves', 999),
        'multiplier': wave_data.get('wave_multiplier', 1.5)
    }

    level_data['enemies'] = {
        'count': wave_data['start_enemies'],
        'types': selected_enemy_types,
        'weights': wave_data['weights'],
        'restricted_area': restricted_area,
        'fixed_positions': []
    }

    return level_data