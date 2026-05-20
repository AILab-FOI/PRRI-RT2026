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
        force_spawn_room=True,
        record_history=False
    ):
        EMPTY = 0
        grid = [[self.WALL for _ in range(width)] for _ in range(height)]
        rooms = []

        history = []

        def snapshot():
            if record_history:
                # shallow copy rows so later mutations do not affect old snapshots
                history.append([row[:] for row in grid])

        # initial full-wall state
        snapshot()

        def carve_room(x, y, w, h):
            y2 = min(y + h, height - 1)
            x2 = min(x + w, width - 1)
            for iy in range(y, y2):
                for ix in range(x, x2):
                    grid[iy][ix] = EMPTY
            snapshot()

        def carve_corridor(x1, y1, x2, y2, avoid_rect=None):
            def dig(cx, cy):
                for dy in range(corridor_thickness):
                    for dx in range(corridor_thickness):
                        tx = cx + dx
                        ty = cy + dy
                        if 0 < tx < width - 1 and 0 < ty < height - 1:
                            if avoid_rect is not None:
                                ax, ay, aw, ah = avoid_rect
                                if ax <= tx < ax + aw and ay <= ty < ay + ah:
                                    continue
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
            snapshot()

        def room_center(room):
            rx, ry, rw, rh = room
            return rx + rw // 2, ry + rh // 2

        # --- 1. Generate normal rooms first ---
        for _ in range(room_count):
            attempts = 0
            while attempts < 40:
                attempts += 1

                base_rw = self.rng.randint(3, 6)
                base_rh = self.rng.randint(3, 5)

                rw = max(3, min(int(base_rw * room_size_multiplier), width - 3))
                rh = max(3, min(int(base_rh * room_size_multiplier), height - 3))

                rx = self.rng.randint(1, width - rw - 2)
                ry = self.rng.randint(1, height - rh - 2)

                new_room = (rx, ry, rw, rh)

                overlap = False
                for ox, oy, ow, oh in rooms:
                    if rx < ox + ow and rx + rw > ox and ry < oy + oh and ry + rh > oy:
                        overlap = True
                        break

                if not overlap:
                    carve_room(rx, ry, rw, rh)
                    rooms.append(new_room)
                    break

        # --- 2. Connect normal rooms with corridors ---
        for i in range(1, len(rooms)):
            x1, y1 = room_center(rooms[i - 1])
            x2, y2 = room_center(rooms[i])
            carve_corridor(x1, y1, x2, y2)

        # --- 3. Place exit in last normal room ---
        if rooms:
            exit_room = rooms[-1]
            ex, ey = room_center(exit_room)
            grid[ey][ex] = self.EXIT
            snapshot()

        player_spawn = (1.5, 1.5)
        spawn_room_rect = None

        # --- 4. Carve 7×7 spawn chamber (5×5 interior) LAST ---
        if force_spawn_room:
            chamber_total_w = 7
            chamber_total_h = 7
            interior_w = 5
            interior_h = 5

            cx = width // 2
            cy = height // 2

            chamber_x = max(1, min(cx - chamber_total_w // 2, width - chamber_total_w - 1))
            chamber_y = max(1, min(cy - chamber_total_h // 2, height - chamber_total_h - 1))

            # Force entire 7×7 as walls
            for iy in range(chamber_y, chamber_y + chamber_total_h):
                for ix in range(chamber_x, chamber_x + chamber_total_w):
                    grid[iy][ix] = self.WALL
            snapshot()

            # Carve 5×5 interior
            interior_x = chamber_x + 1
            interior_y = chamber_y + 1
            for iy in range(interior_y, interior_y + interior_h):
                for ix in range(interior_x, interior_x + interior_w):
                    grid[iy][ix] = EMPTY
            snapshot()

            # Player in center of 5×5 (at 3,3 from top-left of interior)
            player_spawn = (chamber_x + 3 + 0.5, chamber_y + 3 + 0.5)

            # Choose one wall door side
            side = self.rng.choice(["top", "bottom", "left", "right"])
            if side == "top":
                door_x = chamber_x + 3
                door_y = chamber_y
                out_x = door_x
                out_y = door_y - 1
            elif side == "bottom":
                door_x = chamber_x + 3
                door_y = chamber_y + 6
                out_x = door_x
                out_y = door_y + 1
            elif side == "left":
                door_x = chamber_x
                door_y = chamber_y + 3
                out_x = door_x - 1
                out_y = door_y
            else:
                door_x = chamber_x + 6
                door_y = chamber_y + 3
                out_x = door_x + 1
                out_y = door_y

            # Carve doorway tile (1 tile in the wall)
            grid[door_y][door_x] = EMPTY
            snapshot()

            # Carve just outside if in bounds
            if 0 < out_x < width - 1 and 0 < out_y < height - 1:
                grid[out_y][out_x] = EMPTY
                snapshot()

            spawn_room_rect = (chamber_x, chamber_y, chamber_total_w, chamber_total_h)

            # --- 5. Connect spawn to nearest room without carving inside the 7×7 ---
            if rooms:
                nearest_room = min(
                    rooms,
                    key=lambda room: (room_center(room)[0] - out_x) ** 2 +
                                     (room_center(room)[1] - out_y) ** 2
                )
                target_x, target_y = room_center(nearest_room)
                carve_corridor(out_x, out_y, target_x, target_y, avoid_rect=spawn_room_rect)

        # --- 6. Seal borders ---
        for x in range(width):
            grid[0][x] = self.WALL
            grid[height - 1][x] = self.WALL

        for y in range(height):
            grid[y][0] = self.WALL
            grid[y][width - 1] = self.WALL

        snapshot()

        spawn_room = None
        if force_spawn_room and spawn_room_rect is not None:
            # 5×5 interior room info
            spawn_room = (chamber_x + 1, chamber_y + 1, interior_w, interior_h)
            rooms.insert(0, spawn_room)

        return {
            'map': grid,
            'player_spawn': player_spawn,
            'rooms': rooms,
            'history': history if record_history else None
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

    def pick_spawn_chamber_weapon_pos(self, grid, player_pos):
        px, py = int(player_pos[0]), int(player_pos[1])

        offsets = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (-1, 1), (1, -1), (-1, -1),
            (2, 0), (-2, 0), (0, 2), (0, -2)
        ]

        for ox, oy in offsets:
            tx = px + ox
            ty = py + oy
            if 0 <= ty < len(grid) and 0 <= tx < len(grid[0]) and grid[ty][tx] == 0:
                return (tx + 0.5, ty + 0.5)

        return None