import heapq
from collections import deque

def manhattan_distance(cell_a, cell_b):
    """Calculates Manhattan distance heuristic between two cells."""
    return abs(cell_a.row - cell_b.row) + abs(cell_a.col - cell_b.col)


class BFSPathfinder:
    def __init__(self, maze):
        self.maze = maze
        self.is_searching = False
        self.found_path = False

        self.queue = deque()
        self.visited = set()
        self.parent = {}
        self.start_cell = None
        self.goal_cell = None

    def start_search(self, start_cell, goal_cell):
        self.reset()
        self.start_cell = start_cell
        self.goal_cell = goal_cell

        self.queue.append(start_cell)
        self.visited.add(start_cell)
        start_cell.is_visited = True
        self.is_searching = True

    def reset(self):
        self.queue.clear()
        self.visited.clear()
        self.parent.clear()
        self.is_searching = False
        self.found_path = False

        for r in range(self.maze.rows):
            for c in range(self.maze.cols):
                cell = self.maze.grid[r][c]
                cell.is_visited = False
                cell.is_path = False

    def step(self):
        if not self.queue or not self.is_searching:
            self.is_searching = False
            return

        current = self.queue.popleft()

        if current == self.goal_cell:
            self.is_searching = False
            self.found_path = True
            self._reconstruct_path()
            return

        for neighbor in self.maze.get_accessible_neighbors(current):
            if neighbor not in self.visited:
                self.visited.add(neighbor)
                neighbor.is_visited = True
                self.parent[neighbor] = current
                self.queue.append(neighbor)

    def _reconstruct_path(self):
        curr = self.goal_cell
        while curr in self.parent:
            curr.is_path = True
            curr = self.parent[curr]
        self.start_cell.is_path = True


class AStarPathfinder:
    def __init__(self, maze):
        self.maze = maze
        self.is_searching = False
        self.found_path = False

        self.open_set = []
        self.parent = {}
        self.g_score = {}
        self.f_score = {}
        self.counter = 0
        self.start_cell = None
        self.goal_cell = None

    def start_search(self, start_cell, goal_cell):
        self.reset()
        self.start_cell = start_cell
        self.goal_cell = goal_cell

        self.g_score[start_cell] = 0
        self.f_score[start_cell] = manhattan_distance(start_cell, goal_cell)

        heapq.heappush(self.open_set, (self.f_score[start_cell], self.counter, start_cell))
        self.is_searching = True

    def reset(self):
        self.open_set.clear()
        self.parent.clear()
        self.g_score.clear()
        self.f_score.clear()
        self.counter = 0
        self.is_searching = False
        self.found_path = False

        for r in range(self.maze.rows):
            for c in range(self.maze.cols):
                cell = self.maze.grid[r][c]
                cell.is_visited = False
                cell.is_path = False

    def step(self):
        if not self.open_set or not self.is_searching:
            self.is_searching = False
            return

        _, _, current = heapq.heappop(self.open_set)
        current.is_visited = True

        if current == self.goal_cell:
            self.is_searching = False
            self.found_path = True
            self._reconstruct_path()
            return

        for neighbor in self.maze.get_accessible_neighbors(current):
            tentative_g_score = self.g_score.get(current, float('inf')) + 1

            if tentative_g_score < self.g_score.get(neighbor, float('inf')):
                self.parent[neighbor] = current
                self.g_score[neighbor] = tentative_g_score
                self.f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, self.goal_cell)

                if not any(item[2] == neighbor for item in self.open_set):
                    self.counter += 1
                    heapq.heappush(self.open_set, (self.f_score[neighbor], self.counter, neighbor))

    def _reconstruct_path(self):
        curr = self.goal_cell
        path_cells = []
        while curr in self.parent:
            curr.is_path = True
            path_cells.append(curr)
            curr = self.parent[curr]
        self.start_cell.is_path = True
        path_cells.append(self.start_cell)

        path_cells.reverse()
        return path_cells


# --------------------------------------------------------------------------
# Micromouse-style exploration.
#
# Real micromice don't get to see the whole maze. They only know the walls
# right next to whichever cell they're currently standing in (their side
# sensors). To decide where to go, they run a "flood fill": starting from
# the goal, spread outward cell by cell counting steps, but treat any wall
# they haven't personally confirmed as "probably open." That optimism is
# what makes them explore instead of freezing up. Whenever they learn a new
# wall exists, they redo the flood fill and it naturally reroutes them
# (including backing out of dead ends).
#
# Once the goal has been reached once, we switch to a normal shortest-path
# search — but this time using ONLY the walls that were actually confirmed,
# never guessed. That's the "fast run."
# --------------------------------------------------------------------------

DIRS = ['N', 'E', 'S', 'W']
OPPOSITE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
OFFSETS = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}


class FloodFillExplorer:
    def __init__(self, maze):
        self.maze = maze
        self.rows = maze.rows
        self.cols = maze.cols

        self.start_cell = None
        self.goal_cell = None
        self.current_cell = None

        self.is_exploring = False
        self.explore_done = False

        # The robot's own knowledge of the maze.
        # known_walls[(r, c)][direction] is:
        #   True  -> confirmed wall
        #   False -> confirmed open
        #   None  -> not sensed yet (unknown)
        self.known_walls = {
            (r, c): {'N': None, 'E': None, 'S': None, 'W': None}
            for r in range(self.rows) for c in range(self.cols)
        }

        self.flood = {}  # (r, c) -> current estimated distance to goal

    def start_exploration(self, start_cell, goal_cell):
        self.start_cell = start_cell
        self.goal_cell = goal_cell
        self.current_cell = start_cell
        self.is_exploring = True
        self.explore_done = False

        # Clear any leftover visuals from a previous run on this same maze
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.maze.grid[r][c]
                cell.is_visited = False
                cell.is_path = False

    def _sense_cell(self, cell):
        """Reads the REAL walls of the cell the robot is standing on right
        now (this is the equivalent of its physical wall sensors), and also
        tells the neighboring cell about that shared wall, since a real
        mouse's side sensors see both sides of a wall at once."""
        r, c = cell.row, cell.col
        for d in DIRS:
            wall_present = cell.walls[d]
            self.known_walls[(r, c)][d] = wall_present

            dr, dc = OFFSETS[d]
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                self.known_walls[(nr, nc)][OPPOSITE[d]] = wall_present

        cell.is_visited = True

    def _known_open_neighbors(self, cell):
        """Neighbors the robot is CERTAIN it can step into from here."""
        r, c = cell.row, cell.col
        result = []
        for d in DIRS:
            if self.known_walls[(r, c)][d] is False:
                dr, dc = OFFSETS[d]
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    result.append(self.maze.grid[nr][nc])
        return result

    def _recompute_flood(self):
        """BFS outward from the goal using known walls. Any connection
        that hasn't been sensed yet is treated as open (optimistic),
        which is what makes the robot willing to head into unexplored
        territory instead of just refusing to move."""
        self.flood = {(r, c): float('inf') for r in range(self.rows) for c in range(self.cols)}
        goal_key = (self.goal_cell.row, self.goal_cell.col)
        self.flood[goal_key] = 0

        queue = deque([goal_key])
        while queue:
            r, c = queue.popleft()
            dist = self.flood[(r, c)]
            for d in DIRS:
                if self.known_walls[(r, c)][d] is True:
                    continue  # confirmed wall - can't flood through it
                dr, dc = OFFSETS[d]
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.flood[(nr, nc)] > dist + 1:
                        self.flood[(nr, nc)] = dist + 1
                        queue.append((nr, nc))

    def _choose_next_cell(self, current_heading):
        """Among neighbors we KNOW are reachable, pick the one with the
        lowest flood value. Ties favor continuing straight, mimicking a
        real mouse trying to minimize turns."""
        neighbors = self._known_open_neighbors(self.current_cell)
        if not neighbors:
            return None

        best, best_score = None, None
        for n in neighbors:
            dist = self.flood[(n.row, n.col)]
            dr, dc = n.row - self.current_cell.row, n.col - self.current_cell.col
            same_dir = OFFSETS.get(current_heading) == (dr, dc)
            score = (dist, 0 if same_dir else 1)
            if best_score is None or score < best_score:
                best_score, best = score, n
        return best

    def advance(self, current_heading):
        """Call this once every time the robot physically arrives at a
        cell during exploration. Senses the cell, re-floods, and returns
        the next Cell to walk to (or None once the goal is reached)."""
        self._sense_cell(self.current_cell)

        if self.current_cell == self.goal_cell:
            self.is_exploring = False
            self.explore_done = True
            return None

        self._recompute_flood()
        return self._choose_next_cell(current_heading)

    def solve_fastest_known_path(self):
        """Plain BFS shortest path, but ONLY over walls the robot actually
        confirmed while exploring - never a guess. This is the real
        'fast run' a micromouse does after mapping the maze."""
        start_key = (self.start_cell.row, self.start_cell.col)
        goal_key = (self.goal_cell.row, self.goal_cell.col)

        dist = {start_key: 0}
        parent = {}
        queue = deque([start_key])

        while queue:
            r, c = queue.popleft()
            if (r, c) == goal_key:
                break
            for d in DIRS:
                if self.known_walls[(r, c)][d] is False:
                    dr, dc = OFFSETS[d]
                    nr, nc = r + dr, c + dc
                    if (nr, nc) not in dist:
                        dist[(nr, nc)] = dist[(r, c)] + 1
                        parent[(nr, nc)] = (r, c)
                        queue.append((nr, nc))

        if goal_key not in dist:
            return []  # shouldn't happen if exploration actually reached the goal

        path_keys = [goal_key]
        while path_keys[-1] != start_key:
            path_keys.append(parent[path_keys[-1]])
        path_keys.reverse()

        path_cells = [self.maze.grid[r][c] for r, c in path_keys]
        for cell in path_cells:
            cell.is_path = True
        return path_cells