import random

class MapGenerator:
    def __init__(self, seed):
        self.rng = random.Random(seed)

    def generate_map(self, width=20, height=19):
        WALL = 9
        EXIT = 30
        EMPTY = 0

        grid = [[WALL for _ in range(width)] for _ in range(height)]
        rooms = []

        def carve_room(x, y, w, h):
            y2 = min(y + h, height)
            x2 = min(x + w, width)

            for i in range(y, y2):
                for j in range(x, x2):
                    grid[i][j] = EMPTY

        def carve_corridor(x1, y1, x2, y2):
            if self.rng.random() < 0.5:
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    grid[y1][x] = EMPTY
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    grid[y][x2] = EMPTY
            else:
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    grid[y][x1] = EMPTY
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    grid[y2][x] = EMPTY

        for _ in range(7):
            attempts = 0
            while attempts < 40:
                attempts += 1
                rw = self.rng.randint(3, 6)
                rh = self.rng.randint(3, 5)
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

        for i in range(1, len(rooms)):
            x1, y1, w1, h1 = rooms[i - 1]
            x2, y2, w2, h2 = rooms[i]

            cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
            cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2

            carve_corridor(cx1, cy1, cx2, cy2)

        if rooms:
            exit_room = rooms[-1]
            ex = exit_room[0] + exit_room[2] // 2
            ey = exit_room[1] + exit_room[3] // 2
            grid[ey][ex] = EXIT

        for x in range(width):
            grid[0][x] = WALL
            grid[height - 1][x] = WALL

        for y in range(height):
            grid[y][0] = WALL
            grid[y][width - 1] = WALL

        player_spawn = self.pick_player_spawn(rooms, grid)

        return {
            'map': grid,
            'player_spawn': player_spawn,
            'rooms': rooms
        }

    def pick_player_spawn(self, rooms, grid):
        EMPTY = 0
        EXIT = 30

        if not rooms:
            return (1.5, 1.5)

        spawn_room = self.rng.choice(rooms)
        rx, ry, rw, rh = spawn_room

        candidates = []
        for y in range(ry, ry + rh):
            for x in range(rx, rx + rw):
                if grid[y][x] == EMPTY:
                    candidates.append((x, y))

        if not candidates:
            cx = rx + rw // 2
            cy = ry + rh // 2
            return (cx + 0.5, cy + 0.5)

        sx, sy = self.rng.choice(candidates)
        return (sx + 0.5, sy + 0.5)