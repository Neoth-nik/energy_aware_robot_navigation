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

        self.open_set = []  # Min-heap priority queue storing (f_score, counter, cell)
        self.parent = {}
        self.g_score = {}
        self.f_score = {}
        self.counter = 0  # Tie-breaker counter for heap sorting
        self.start_cell = None
        self.goal_cell = None

    def start_search(self, start_cell, goal_cell):
        self.reset()
        self.start_cell = start_cell
        self.goal_cell = goal_cell

        # Initialize g_score (distance from start) and f_score (g_score + heuristic)
        self.g_score[start_cell] = 0
        self.f_score[start_cell] = manhattan_distance(start_cell, goal_cell)

        # Push start node into priority queue
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

        # Pop cell with the lowest f_score
        _, _, current = heapq.heappop(self.open_set)
        current.is_visited = True

        if current == self.goal_cell:
            self.is_searching = False
            self.found_path = True
            self._reconstruct_path()
            return

        for neighbor in self.maze.get_accessible_neighbors(current):
            # Base step cost = 1
            tentative_g_score = self.g_score.get(current, float('inf')) + 1

            if tentative_g_score < self.g_score.get(neighbor, float('inf')):
                self.parent[neighbor] = current
                self.g_score[neighbor] = tentative_g_score
                self.f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, self.goal_cell)

                # Push to open set if not present
                if not any(item[2] == neighbor for item in self.open_set):
                    self.counter += 1
                    heapq.heappush(self.open_set, (self.f_score[neighbor], self.counter, neighbor))

    # Add this return inside _reconstruct_path() method in pathfinding.py:
    def _reconstruct_path(self):
        curr = self.goal_cell
        path_cells = []
        while curr in self.parent:
            curr.is_path = True
            path_cells.append(curr)
            curr = self.parent[curr]
        self.start_cell.is_path = True
        path_cells.append(self.start_cell)
    
        path_cells.reverse() # Start to Goal order
        return path_cells  