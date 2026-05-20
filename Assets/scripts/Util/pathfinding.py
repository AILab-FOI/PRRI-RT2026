from collections import deque


class PathFinding:
    def __init__(self, game):
        self.game = game
        self.map = game.map.mini_map
        self.ways = [-1, 0], [0, -1], [1, 0], [0, 1], [-1, -1], [1, -1], [1, 1], [-1, 1]
        self.graph = {}
        self.get_graph()
        self.flow_field = {}
        self.target_pos = None

    def update(self):
        """Update the global flow field radiating from the player's position."""
        new_target = self.game.player.map_pos
        
        if new_target == self.target_pos:
            return
            
        self.target_pos = new_target
        if self.target_pos not in self.graph:
            self.target_pos = self.find_closest_valid_position(self.target_pos)

        self._calculate_flow_field()

    def _calculate_flow_field(self):
        queue = deque([self.target_pos])
        self.flow_field = {self.target_pos: None}

        while queue:
            cur_node = queue.popleft()

            for next_node in self.graph.get(cur_node, []):
                if next_node not in self.flow_field:
                    queue.append(next_node)
                    self.flow_field[next_node] = cur_node

    def get_next_step(self, pos):
        """Get the next step for an NPC at 'pos' towards the player."""
        if pos not in self.flow_field:
            return pos
            
        next_step = self.flow_field[pos]
        
        if next_step is None:
            return pos
            
        return next_step

    def find_closest_valid_position(self, pos):
        x, y = pos
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                new_pos = (x + dx, y + dy)
                if new_pos in self.graph:
                    return new_pos
        if self.graph:
            return next(iter(self.graph))
        return pos

    def get_next_nodes(self, x, y):
        return [(x + dx, y + dy) for dx, dy in self.ways if (x + dx, y + dy) not in self.game.map.world_map]

    def get_graph(self):
        self.graph = {}
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if (x, y) not in self.game.map.world_map:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)

    def update_graph(self):
        self.map = self.game.map.mini_map
        self.get_graph()
        self.target_pos = None # Force recalculation on next update