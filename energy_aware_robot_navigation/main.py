import pygame
import random

pygame.init()

# Window and Grid Dimensions
WIDTH = 800
HEIGHT = 600
ROWS = 25
COLS = 25

# Dynamically calculate cell size & position
CELL_SIZE = min(WIDTH // COLS, (HEIGHT - 50) // ROWS)
OFFSET_X = (WIDTH - (COLS * CELL_SIZE)) // 2
OFFSET_Y = ((HEIGHT - 50) - (ROWS * CELL_SIZE)) // 2 + 50

# Visual Palette
BG_COLOR = (18, 18, 24)           # Dark Theme Screen
GRID_BG = (30, 34, 42)            # Unvisited Cell
IN_MAZE_COLOR = (245, 247, 250)   # Carved Path
FRONTIER_COLOR = (255, 127, 80)   # Active Frontier Wall/Cell (Coral/Orange)
CURRENT_COLOR = (0, 210, 255)     # Current Active Cell (Electric Cyan)
START_COLOR = (46, 204, 113)      # Start Cell (Green)
END_COLOR = (231, 76, 60)         # End Cell (Red)
WALL_COLOR = (15, 15, 20)         # Wall line color
TEXT_COLOR = (200, 210, 225)      # UI Text

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Real-Time Prim's Maze Generation Visualizer")

# Font for HUD instructions
font = pygame.font.SysFont("Consolas", 18, bold=True)


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.walls = {'N': True, 'E': True, 'S': True, 'W': True}
        self.in_maze = False
        self.is_frontier = False
        self.is_current = False


class PrimMazeGenerator:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.reset()

    def reset(self):
        """Resets the grid back to initial state."""
        self.grid = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.frontier = []
        self.is_generating = False
        self.current_cell = None

    def start_generation(self, start_row=0, start_col=0):
        """Initializes the Prim's algorithm generation process starting at top-left."""
        self.reset()
        self.is_generating = True

        start_cell = self.grid[start_row][start_col]
        start_cell.in_maze = True
        self.current_cell = start_cell
        start_cell.is_current = True
        
        self._add_cell_walls_to_frontier(start_cell)

    def _add_cell_walls_to_frontier(self, cell):
        r, c = cell.row, cell.col
        directions = [('N', -1, 0), ('E', 0, 1), ('S', 1, 0), ('W', 0, -1)]

        for d, dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbor = self.grid[nr][nc]
                if not neighbor.in_maze:
                    neighbor.is_frontier = True
                    self.frontier.append((r, c, d))

    def step(self):
        """Executes a single step of Prim's algorithm for animation."""
        if not self.frontier or not self.is_generating:
            self.is_generating = False
            if self.current_cell:
                self.current_cell.is_current = False
            return

        # Pick a random wall from the frontier list
        wall_idx = random.randint(0, len(self.frontier) - 1)
        r, c, direction = self.frontier.pop(wall_idx)

        cell_a = self.grid[r][c]
        opposite = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
        dir_offsets = {'N': (-1, 0), 'E': (0, 1), 'S': (1, 0), 'W': (0, -1)}
        dr, dc = dir_offsets[direction]
        nr, nc = r + dr, c + dc

        if 0 <= nr < self.rows and 0 <= nc < self.cols:
            cell_b = self.grid[nr][nc]

            if cell_a.in_maze != cell_b.in_maze:
                new_cell = cell_b if not cell_b.in_maze else cell_a
                
                # Clear visual state of former current cell
                if self.current_cell:
                    self.current_cell.is_current = False

                # Carve walls
                cell_a.walls[direction] = False
                cell_b.walls[opposite[direction]] = False
                
                # Update cell states
                new_cell.in_maze = True
                new_cell.is_frontier = False
                new_cell.is_current = True
                self.current_cell = new_cell

                # Add new cell's neighbors to frontier
                self._add_cell_walls_to_frontier(new_cell)

    def draw(self, surface):
        """Renders grid cells and wall lines onto screen."""
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                x = OFFSET_X + c * CELL_SIZE
                y = OFFSET_Y + r * CELL_SIZE

                # Dynamic background colors based on generation state
                if r == 0 and c == 0:
                    color = START_COLOR  # Start (Green)
                elif r == self.rows - 1 and c == self.cols - 1:
                    color = END_COLOR    # End (Red)
                elif cell.is_current:
                    color = CURRENT_COLOR
                elif cell.is_frontier:
                    color = FRONTIER_COLOR
                elif cell.in_maze:
                    color = IN_MAZE_COLOR
                else:
                    color = GRID_BG

                pygame.draw.rect(surface, color, (x, y, CELL_SIZE, CELL_SIZE))

                # Draw cell walls (Skip exterior entrance/exit borders for clarity)
                if cell.walls['N'] and not (r == 0 and c == 0):
                    pygame.draw.line(surface, WALL_COLOR, (x, y), (x + CELL_SIZE, y), 2)
                if cell.walls['E']:
                    pygame.draw.line(surface, WALL_COLOR, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
                if cell.walls['S'] and not (r == self.rows - 1 and c == self.cols - 1):
                    pygame.draw.line(surface, WALL_COLOR, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
                if cell.walls['W']:
                    pygame.draw.line(surface, WALL_COLOR, (x, y), (x, y + CELL_SIZE), 2)


# Instantiate generator
maze_gen = PrimMazeGenerator(ROWS, COLS)
clock = pygame.time.Clock()

# Main program loop
running = True

while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                # Start real-time generation starting at (0, 0)
                maze_gen.start_generation(start_row=0, start_col=0)

            elif event.key == pygame.K_r:
                maze_gen.reset()

    # 2. Algorithm Step Update (animates steps)
    if maze_gen.is_generating:
        maze_gen.step()
        maze_gen.step()

    # 3. Render Graphics
    screen.fill(BG_COLOR)
    maze_gen.draw(screen)

    # Status Banner
    status = "STATUS: GENERATING..." if maze_gen.is_generating else "STATUS: IDLE"
    hud_text = font.render(f"Press 'G' to Generate Maze | 'R' to Reset | {status}", True, TEXT_COLOR)
    screen.blit(hud_text, (OFFSET_X, 15))

    # 4. Display & Clock
    pygame.display.flip()
    clock.tick(60)

pygame.quit()