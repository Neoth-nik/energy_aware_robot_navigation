import pygame
from pathfinding import FloodFillExplorer, BFSPathfinder, AStarPathfinder
from maze import (
    WIDTH, HEIGHT, ROWS, COLS, OFFSET_X, BG_COLOR, TEXT_COLOR,
    PrimMazeGenerator
)
from pathfinding import FloodFillExplorer
from robot import Robot

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Navigation Visualizer")
font = pygame.font.SysFont("Consolas", 15, bold=True)

maze_gen = PrimMazeGenerator(ROWS, COLS)
robot = Robot(start_row=0, start_col=0)
explorer = FloodFillExplorer(maze_gen)
bfs_solver = BFSPathfinder(maze_gen)
astar_solver = AStarPathfinder(maze_gen)
active_solver = None

# mode: 'idle' | 'exploring' | 'explore_done' | 'fast_run' | 'finished'
mode = 'idle'

clock = pygame.time.Clock()
running = True


def full_reset():
    global explorer, mode, active_solver
    robot.reset()
    explorer = FloodFillExplorer(maze_gen)
    bfs_solver.reset()
    astar_solver.reset()
    active_solver = None
    mode = 'idle'

while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                full_reset()
                maze_gen.start_generation(start_row=0, start_col=0)

            elif event.key == pygame.K_r:
                full_reset()
                maze_gen.reset()

            elif event.key == pygame.K_e:
                if not maze_gen.is_generating:
                    robot.reset()
                    explorer = FloodFillExplorer(maze_gen)
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    explorer.start_exploration(start_cell, goal_cell)
                    mode = 'exploring'
            elif event.key == pygame.K_b:
                if not maze_gen.is_generating:
                    full_reset()
                    active_solver = bfs_solver
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    bfs_solver.start_search(start_cell, goal_cell)
                    mode = 'bfs_solving'

            elif event.key == pygame.K_a:
                if not maze_gen.is_generating:
                    full_reset()
                    active_solver = astar_solver
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    astar_solver.start_search(start_cell, goal_cell)
                    mode = 'astar_solving'

    # 2. Simulation Update
    if maze_gen.is_generating:
        maze_gen.step()
        maze_gen.step()

    elif mode == 'exploring':
        # Robot only decides its next move once it has physically
        # arrived at a cell (i.e. it's not mid-step between cells).
        if not robot.is_moving:
            explorer.current_cell = maze_gen.grid[robot.row][robot.col]
            next_cell = explorer.advance(robot.heading)

            if next_cell is not None:
                robot.set_path([next_cell])
            else:
                mode = 'explore_done'
    elif mode == 'bfs_solving' or mode == 'astar_solving':
        if active_solver.is_searching:
            active_solver.step()
            active_solver.step()
            if active_solver.found_path and not robot.is_moving and not robot.path:
                path_nodes = active_solver._reconstruct_path()
                robot.set_path(path_nodes)
        elif not robot.is_moving:
            mode = 'finished' 

    elif mode == 'explore_done':
        fastest_path = explorer.solve_fastest_known_path()
        robot.reset(start_row=0, start_col=0)
        if fastest_path:
            robot.set_path(fastest_path)
        mode = 'fast_run'

    elif mode == 'fast_run':
        if not robot.is_moving:
            mode = 'finished'

    # Exploration moves cell-by-cell (slower feel), fast run is snappier
    if mode == 'exploring':
        robot.update(speed=0.30)
    else:
        robot.update(speed=0.18)
    # 3. Render Graphics
    screen.fill(BG_COLOR)
    maze_gen.draw(screen)
    robot.draw(screen)

    if maze_gen.is_generating:
        status = "GENERATING MAZE..."
    elif mode == 'exploring':
        status = "EXPLORING (mapping walls as it goes)..."
    elif mode == 'fast_run':
        status = "FAST RUN (using the map it built)..."
    elif mode == 'finished':
        status = "FAST RUN COMPLETE!"
    elif mode == 'bfs_solving':
        status = "RUNNING BFS (full maze knowledge)..."
    elif mode == 'astar_solving':
        status = "RUNNING A* (full maze knowledge)..."
    else:
        status = "IDLE"

    hud_text = font.render(
    f"[G] Generate | [E] Micromouse Explore | [B] BFS | [A] A* | [R] Reset | {status}",
    True, TEXT_COLOR)

    screen.blit(hud_text, (OFFSET_X, 10))

    # 4. Display & Clock
    pygame.display.flip()
    clock.tick(60)

pygame.quit()