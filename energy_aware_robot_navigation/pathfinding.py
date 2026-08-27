from collections import deque

class BFSPathfinder:
    def __init__(self, maze):
        self.maze = maze
        self.is_searching = False
        self.found_path = False
        
        # BFS Data Structures
        self.queue = deque()
        self.visited = set()
        self.parent = {}
        self.start_cell = None
        self.goal_cell = None

    def start_search(self, start_cell, goal_cell):
        """Initializes BFS algorithm parameters."""
        self.reset()
        self.start_cell = start_cell
        self.goal_cell = goal_cell
        
        self.queue.append(start_cell)
        self.visited.add(start_cell)
        start_cell.is_visited = True
        self.is_searching = True

    def reset(self):
        """Resets the search states across the grid."""
        self.queue.clear()
        self.visited.clear()
        self.parent.clear()
        self.is_searching = False
        self.found_path = False

        # Reset visual pathfinding flags on all grid cells
        for r in range(self.maze.rows):
            for c in range(self.maze.cols):
                cell = self.maze.grid[r][c]
                cell.is_visited = False
                cell.is_path = False

    def step(self):
        """Executes a single step of BFS for real-time visualization."""
        if not self.queue or not self.is_searching:
            self.is_searching = False
            return

        current = self.queue.popleft()

        # Goal reached
        if current == self.goal_cell:
            self.is_searching = False
            self.found_path = True
            self._reconstruct_path()
            return

        # Explore accessible neighbors (where walls are carved open)
        for neighbor in self.maze.get_accessible_neighbors(current):
            if neighbor not in self.visited:
                self.visited.add(neighbor)
                neighbor.is_visited = True
                self.parent[neighbor] = current
                self.queue.append(neighbor)

    def _reconstruct_path(self):
        """Backtracks from goal to start to highlight the final shortest path."""
        curr = self.goal_cell
        while curr in self.parent:
            curr.is_path = True
            curr = self.parent[curr]
        self.start_cell.is_path = True  # Highlight start cell