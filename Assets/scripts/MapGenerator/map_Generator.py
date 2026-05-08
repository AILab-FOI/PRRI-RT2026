import random
import math


class MapGenerator:
    def __init__(self, seed, wall_id=9, exit_id=30):
        self.rng = random.Random(seed)
        self.WALL = wall_id
        self.EXIT = exit_id

    def generate_map(
        self,
        width=20,
        height=19,
        room_size_multiplier=1.0,
        room_count=7,
        corridor_thickness=1,
        force_spawn_room=True
    ):
        EMPTY = 0
        grid = [[self.WALL for _ in range(width)] for _ in range(height)]
        rooms = []

        def carve_room(x, y, w, h):
            y2 = min(y + h, height - 1)
            x2 = min(x + w, width - 1)
            for iy in range(y, y2):
                for ix in range(x, x2):
                    grid[iy][ix] = EMPTY

        def carve_corridor(x1, y1, x2, y2):
            def dig(cx, cy):
                for dy in range(corridor_thickness):
                    for dx in range(corridor_thickness):
                        tx = cx + dx
                        ty = cy + dy
                        if 0 < tx < width - 1 and 0 < ty < height - 1:
                            grid[ty][tx] = EMPTY

            if self.rng.random() < 0.5:
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    dig(x, y1)
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    dig(x2, y)
            else:
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    dig(x1, y)
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    dig(x, y2)

        def room_center(room):
            rx, ry, rw, rh = room
            return rx + rw // 2, ry + rh // 2

        # 1. Generate normal rooms first
        for _ in range(room_count):
            attempts = 0
            while attempts < 40:
                attempts += 1

                base_rw = self.rng.randint(3, 6)
                base_rh = self.rng.randint(3, 5)

                rw = int(base_rw * room_size_multiplier)
                rh = int(base_rh * room_size_multiplier)

                rw = max(3, min(rw, width - 3))
                rh = max(3, min(rh, height - 3))

                rx = self.rng.randint(1, width - rw - 2)
                ry = self.rng.randint(1, height - rh - 2)

                new_room = (rx, ry, rw, rh)
                overlap = False

                for ox, oy, ow, oh in rooms:
                    if (
                        rx < ox + ow and rx + rw > ox and
                        ry < oy + oh and ry + rh > oy
                    ):
                        overlap = True
                        break

                if not overlap:
                    carve_room(rx, ry, rw, rh)
                    rooms.append(new_room)
                    break

        # 2. Connect normal rooms first
        for i in range(1, len(rooms)):
            x1, y1 = room_center(rooms[i - 1])
            x2, y2 = room_center(rooms[i])
            carve_corridor(x1, y1, x2, y2)

        # 3. Put exit in the last normal room
        if rooms:
            exit_room = rooms[-1]
            ex, ey = room_center(exit_room)
            grid[ey][ex] = self.EXIT

        spawn_room = None
        spawn_door_inside = None
        spawn_door_outside = None
        player_spawn = (1.5, 1.5)

        # 4. Carve the spawn chamber LAST so it cannot be overwritten
        if force_spawn_room:
            chamber_total_w = 5
            chamber_total_h = 5

            cx = width // 2
            cy = height // 2

            chamber_x = max(1, min(cx - chamber_total_w // 2, width - chamber_total_w - 1))
            chamber_y = max(1, min(cy - chamber_total_h // 2, height - chamber_total_h - 1))

            # rebuild 5x5 as solid walls
            for iy in range(chamber_y, chamber_y + chamber_total_h):
                for ix in range(chamber_x, chamber_x + chamber_total_w):
                    grid[iy][ix] = self.WALL

            # carve 3x3 interior
            for iy in range(chamber_y + 1, chamber_y + 4):
                for ix in range(chamber_x + 1, chamber_x + 4):
                    grid[iy][ix] = EMPTY

            # center of 3x3 interior
            player_spawn = (chamber_x + 2 + 0.5, chamber_y + 2 + 0.5)

            # one exit tile in a random wall
            side = self.rng.choice(["top", "bottom", "left", "right"])
            if side == "top":
                door_x = chamber_x + 2
                door_y = chamber_y
                out_x = door_x
                out_y = door_y - 1
            elif side == "bottom":
                door_x = chamber_x + 2
                door_y = chamber_y + 4
                out_x = door_x
                out_y = door_y + 1
            elif side == "left":
                door_x = chamber_x
                door_y = chamber_y + 2
                out_x = door_x - 1
                out_y = door_y
            else:
                door_x = chamber_x + 4
                door_y = chamber_y + 2
                out_x = door_x + 1
                out_y = door_y

            grid[door_y][door_x] = EMPTY
            if 0 < out_x < width - 1 and 0 < out_y < height - 1:
                grid[out_y][out_x] = EMPTY

            spawn_room = (chamber_x + 1, chamber_y + 1, 3, 3)
            spawn_door_inside = (door_x, door_y)
            spawn_door_outside = (out_x, out_y)

            # 5. Connect spawn room to nearest normal room
            if rooms and spawn_door_outside is not None:
                nearest_room = min(
                    rooms,
                    key=lambda room: (room_center(room)[0] - spawn_door_outside[0]) ** 2 +
                                     (room_center(room)[1] - spawn_door_outside[1]) ** 2
                )
                target_x, target_y = room_center(nearest_room)
                carve_corridor(spawn_door_outside[0], spawn_door_outside[1], target_x, target_y)

        # 6. Seal borders again
        for x in range(width):
            grid[0][x] = self.WALL
            grid[height - 1][x] = self.WALL

        for y in range(height):
            grid[y][0] = self.WALL
            grid[y][width - 1] = self.WALL

        # add spawn room to rooms list only after everything is done
        if spawn_room is not None:
            rooms.insert(0, spawn_room)

        return {
            'map': grid,
            'player_spawn': player_spawn,
            'rooms': rooms
        }

    def pick_random_locations(self, grid, count, exclude_positions):
        EMPTY = 0
        excluded_tiles = {(int(px), int(py)) for px, py in exclude_positions}
        candidates = []

        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if grid[y][x] == EMPTY and (x, y) not in excluded_tiles:
                    candidates.append((x + 0.5, y + 0.5))

        if count > len(candidates):
            return candidates

        return self.rng.sample(candidates, count)

    def pick_position_in_front_of_player(self, grid, player_pos, player_angle, distance_tiles=2):
        px, py = player_pos

        tx = int(px + math.cos(player_angle) * distance_tiles)
        ty = int(py + math.sin(player_angle) * distance_tiles)

        if 0 <= ty < len(grid) and 0 <= tx < len(grid[0]) and grid[ty][tx] == 0:
            return (tx + 0.5, ty + 0.5)

        tx = int(px + math.cos(player_angle) * 1)
        ty = int(py + math.sin(player_angle) * 1)
        if 0 <= ty < len(grid) and 0 <= tx < len(grid[0]) and grid[ty][tx] == 0:
            return (tx + 0.5, ty + 0.5)

        offsets = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (-1, 1), (1, -1), (-1, -1),
            (2, 0), (-2, 0), (0, 2), (0, -2)
        ]

        for ox, oy in offsets:
            tx = int(px) + ox
            ty = int(py) + oy
            if 0 <= ty < len(grid) and 0 <= tx < len(grid[0]) and grid[ty][tx] == 0:
                return (tx + 0.5, ty + 0.5)

        return None