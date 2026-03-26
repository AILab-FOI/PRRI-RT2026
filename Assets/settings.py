import math

# game settings
RES = WIDTH, HEIGHT = 1600, 900
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 0

# Default player positions for each level
PLAYER_POS = 5.5, 1.5           #uvodni level
PLAYER_POS_LEVEL2 = 1.5, 2.5    #lvl 1
PLAYER_POS_LEVEL3 = 1.5, 2.5    #lvl 2
PLAYER_POS_LEVEL4 = 17.5, 1.5   #lvl 3
PLAYER_POS_LEVEL5 = 13.5, 1.5   #lvl 4

PLAYER_ANGLE = 0
PLAYER_SPEED = 0.004
PLAYER_ROT_SPEED = 0.002
PLAYER_SIZE_SCALE = 60
PLAYER_MAX_HEALTH = 100

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

# Default floor color
FLOOR_COLOR = (30, 30, 30)

# Floor colors for different levels
FLOOR_COLORS = {
    1: (216, 217, 217), #level 1 white
    2: (30, 30, 30),  # Level 1: Dark gray
    3: (216, 217, 217),  # Level 2: White
    4: (30, 30, 30),  # Level 3: Dark gray (same as default)
    5: (30, 30, 30),  # Level 3: Dark gray (same as default)
}

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2