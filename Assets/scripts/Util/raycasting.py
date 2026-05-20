import pygame as pg
import math
from Assets.settings import *


class RayCasting:
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []
        self.objects_to_render = []
        self.textures = self.game.object_renderer.wall_textures

    def get_objects_to_render(self):
        self.objects_to_render = []
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values

            if proj_height < 0:
                proj_height = 0

            if proj_height < HEIGHT:
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), 0, SCALE, TEXTURE_SIZE
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, proj_height))
                wall_pos = (ray * SCALE, HALF_HEIGHT - proj_height // 2)
            else:
                texture_height = TEXTURE_SIZE * HEIGHT / proj_height
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), HALF_TEXTURE_SIZE - texture_height // 2,
                    SCALE, texture_height
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, HEIGHT))
                wall_pos = (ray * SCALE, 0)

            self.objects_to_render.append((depth, wall_column, wall_pos))
    '''
    def ray_cast(self):
        self.ray_casting_result = []
        texture_vert, texture_hor = 1, 1
        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.game.player.angle - HALF_FOV + 0.0001
        for ray in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            # horizontals
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a

            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.game.map.world_map:
                    texture_hor = self.game.map.world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            # verticals
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.game.map.world_map:
                    texture_vert = self.game.map.world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            # depth, texture offset
            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor

            # remove fishbowl effect
            depth *= math.cos(self.game.player.angle - ray_angle)

            # projection
            proj_height = SCREEN_DIST / (depth + 0.0001)

            # ray casting result
            self.ray_casting_result.append((depth, proj_height, texture, offset))

            ray_angle += DELTA_ANGLE
    '''

    def ray_cast(self):
        result = self.ray_casting_result
        result.clear()
        append = result.append

        px, py = self.game.player.pos
        world = self.game.map.world_map

        angle = self.game.player.angle
        dir_x = math.cos(angle)
        dir_y = math.sin(angle)

        plane_len = math.tan(FOV / 2)
        plane_x = -dir_y * plane_len
        plane_y = dir_x * plane_len

        inv_num = 2.0 / NUM_RAYS
        max_steps = MAX_DEPTH * 4
        _floor = math.floor

        for ray in range(NUM_RAYS):
            camera_x = ray * inv_num - 1
            ray_dir_x = dir_x + plane_x * camera_x
            ray_dir_y = dir_y + plane_y * camera_x

            mx = int(px)
            my = int(py)

            delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else 1e30
            delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else 1e30

            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (px - mx) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (mx + 1.0 - px) * delta_dist_x

            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (py - my) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (my + 1.0 - py) * delta_dist_y

            hit = False
            side = 0
            texture = 1

            for _ in range(max_steps):
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    mx += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    my += step_y
                    side = 1

                wall_val = world.get((mx, my))
                if wall_val:
                    texture = wall_val
                    hit = True
                    break

            if not hit:
                continue

            if side == 0:
                perp_depth = side_dist_x - delta_dist_x
                wall_x = py + perp_depth * ray_dir_y
            else:
                perp_depth = side_dist_y - delta_dist_y
                wall_x = px + perp_depth * ray_dir_x

            wall_x -= _floor(wall_x)

            if side == 0:
                offset = wall_x if ray_dir_x < 0 else (1 - wall_x)
            else:
                offset = (1 - wall_x) if ray_dir_y < 0 else wall_x

            proj_height = SCREEN_DIST / (perp_depth + 0.0001)

            append((perp_depth, proj_height, texture, offset))

    def update(self):
        self.ray_cast()
        self.get_objects_to_render()