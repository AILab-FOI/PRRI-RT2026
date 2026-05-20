import sys
import os
import numpy as np
import pygame
import imageio.v2 as imageio

from Assets.scripts.MapGenerator.runtime_level import build_runtime_level  # adjust path
from Assets import settings as s


TILE_SIZE = 16
WALL_COLOR = (40, 40, 40)
FLOOR_COLOR = (200, 200, 200)
EXIT_COLOR = (0, 200, 0)


def grid_to_surface(grid, wall_id, exit_id):
    height = len(grid)
    width = len(grid[0])

    surf = pygame.Surface((width * TILE_SIZE, height * TILE_SIZE))
    surf.fill((0, 0, 0))

    for y in range(height):
        for x in range(width):
            val = grid[y][x]
            if val == wall_id:
                color = WALL_COLOR
            elif val == exit_id:
                color = EXIT_COLOR
            else:
                color = FLOOR_COLOR
            pygame.draw.rect(
                surf,
                color,
                pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            )

    return surf


def build_gif_for_seed(seed, level_id=99, out_path="map_generation.gif", frames_per_step=5, frame_duration=0.05):
    pygame.init()

    level_data = build_runtime_level(seed, level_id)
    history = level_data.get("map_history", [])

    if not history:
        print("No history recorded. Make sure record_history=True in MapGenerator.generate_map.")
        return

    # Get tile ids from settings
    tile_set = s.PROCEDURAL_TILE_SET.get(level_id, {'wall': 9, 'exit': 30})
    wall_id = tile_set['wall']
    exit_id = tile_set['exit']

    gif_frames = []

    for grid_state in history:
        surf = grid_to_surface(grid_state, wall_id, exit_id)
        arr = pygame.surfarray.array3d(surf)  # (w, h, 3)
        arr = np.transpose(arr, (1, 0, 2))    # (h, w, 3)
        for _ in range(frames_per_step):
            gif_frames.append(arr)

    imageio.mimsave(out_path, gif_frames, duration=frame_duration,loop = 0)
    print(f"Saved GIF to {out_path}")

    pygame.quit()


if __name__ == "__main__":
    # Usage:
    #   python make_map_gif.py [seed] [level_id] [output.gif]
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 123
    level_id = int(sys.argv[2]) if len(sys.argv) > 2 else 99
    out_path = sys.argv[3] if len(sys.argv) > 3 else f"map_generation_{seed}_lvl{level_id}.gif"

    build_gif_for_seed(seed, level_id, out_path)