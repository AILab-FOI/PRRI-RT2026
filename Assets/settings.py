import math

# game settings
RES = WIDTH, HEIGHT = 1600, 900
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 144

# Default player positions for each level
PLAYER_POS = 1.5, 1.5          #uvodni level (Level 1)
PLAYER_POS_LEVEL2 = 1.5, 1.5    #lvl 2 
PLAYER_POS_LEVEL3 = 1.5, 2.5    #lvl 3 
PLAYER_POS_LEVEL4 = 1.5, 1.5   #lvl 4
PLAYER_POS_LEVEL5 = 13.5, 1.5   #lvl 5 
PLAYER_POS_LEVEL6 = 9.5, 2.5    #lvl 6 
PLAYER_ANGLE = 0
PLAYER_SPEED = 0.004
PLAYER_ROT_SPEED = 0.002
PLAYER_SIZE_SCALE = 60
PLAYER_MAX_HEALTH = 100
PLAYER_BASE_HEAL = 20

# dash settings
PLAYER_DASH_MULTIPLIER = 3.0
PLAYER_DASH_DURATION = 200
PLAYER_DASH_COOLDOWN = 1000

# powerup settings
POWERUP_INVULNERABILITY_DURATION = 5000
POWERUP_PICKUP_DISTANCE = 0.5

# UI settings - percentage-based margins
UI_MARGIN_PERCENT_X = 0.03
UI_MARGIN_PERCENT_Y = 0.03

MOUSE_SENSITIVITY = 0.0003
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

#Weapon Data
AMMO_SMG_STARTING_BAG = 60
AMMO_PISTOL_STARTING_BAG = 21

AMMO_SMG_DROP_COUNT = 30
AMMO_PISTOL_DROP_COUNT = 14

# Default floor color
FLOOR_COLOR = (30, 30, 30)

# Floor colors for different levels
FLOOR_COLORS = {
    1: (30, 30, 30), #level 1 dark space match
    2: (30, 30, 30),  # Level 1: Dark gray
    3: (20, 22, 25),  # Level 2: Tamno siva usklađena s novom teksturom zida
    4: (30, 30, 30),  # Level 3: Dark gray (same as default)
    5: (30, 30, 30),  # Level 3: Dark gray (same as default)
}
CEILING_COLORS = {
    1: (20, 20, 20),
    2: (40, 40, 45),
    3: (30, 35, 40),
    4: (25, 25, 30),
    5: (18, 18, 22),
    6: (18, 18, 22),
}

LEVEL_ROTATION = {
    1: math.radians(90),
    2: math.radians(90),
    3: math.radians(90),
    4: 0.0,
    5: 0.0,
    6: 0.0,
}

FOV = math.radians(75) #75 fov default
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20



SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2


PROCEDURAL_MAP_SIZE = {
    99: (40, 40)  # Massive map!
}

PROCEDURAL_TILE_SET = {
    99: {'wall': 9, 'exit': 30}
}

PROCEDURAL_WAVES = {
    99: {
        'total_waves': 999, 
        'start_enemies': 25, 
        'wave_multiplier': 1.5, 
        'types': ['StakorNPC', 'KlonoviNPC'], 
        'weights': [70, 30],
        'safe_spawn_radius': 15  # Enemies cannot spawn within 12 tiles of the player
    }
}

PROCEDURAL_ITEMS = {
    99: {'weapons': 2, 'heals': 5, 'ammo': 6}
}

PROCEDURAL_ROOM_SETTINGS = {
    99: {
        'size_multiplier': 1.5,
        'room_count': 15,
        'corridor_thickness': 2,
        'force_spawn_room': True
    }
}

NPC_DROP_SETTINGS = {
    'enabled': True,
    'drop_chance': 15,
    'item_weights': {
        'heal': 5,
        'ammo': 20,
        'powerups': 10,
        'bat': 20  #postotak za palicu spawn, treba smanjit na rare
    }
}