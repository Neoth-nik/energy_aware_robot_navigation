import pygame
from maze import (
    WIDTH, HEIGHT, ROWS, COLS, OFFSET_X, BG_COLOR, TEXT_COLOR,
    PrimMazeGenerator
)
from pathfinding import BFSPathfinder, AStarPathfinder

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Navigation Visualizer - BFS & A*")
font = pygame.font.SysFont("Consolas", 15, bold=True)

# Instantiate generator & pathfinders
maze_gen = PrimMazeGenerator(ROWS, COLS)
bfs_solver = BFSPathfinder(maze_gen)
astar_solver = AStarPathfinder(maze_gen)

active_solver = None
clock = pygame.time.Clock()

running = True

while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                bfs_solver.reset()
                astar_solver.reset()
                active_solver = None
                maze_gen.start_generation(start_row=0, start_col=0)

            elif event.key == pygame.K_r:
                bfs_solver.reset()
                astar_solver.reset()
                active_solver = None
                maze_gen.reset()

            elif event.key == pygame.K_b:
                if not maze_gen.is_generating:
                    bfs_solver.reset()
                    astar_solver.reset()
                    active_solver = bfs_solver
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    bfs_solver.start_search(start_cell, goal_cell)

            elif event.key == pygame.K_a:
                if not maze_gen.is_generating:
                    bfs_solver.reset()
                    astar_solver.reset()
                    active_solver = astar_solver
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    astar_solver.start_search(start_cell, goal_cell)

    # 2. Algorithm Step Updates (Animation)
    if maze_gen.is_generating:
        maze_gen.step()
        maze_gen.step()
    elif active_solver and active_solver.is_searching:
        active_solver.step()
        active_solver.step()

    # 3. Render Graphics
    screen.fill(BG_COLOR)
    maze_gen.draw(screen)

    # Status Banner
    if maze_gen.is_generating:
        status = "STATUS: GENERATING MAZE..."
    elif active_solver and active_solver.is_searching:
        solver_name = "BFS" if active_solver == bfs_solver else "A*"
        status = f"STATUS: RUNNING {solver_name}..."
    elif active_solver and active_solver.found_path:
        solver_name = "BFS" if active_solver == bfs_solver else "A*"
        status = f"STATUS: {solver_name} PATH FOUND!"
    else:
        status = "STATUS: IDLE"

    hud_text = font.render(f"[G] Gen | [B] BFS | [A] A* | [R] Reset | {status}", True, TEXT_COLOR)
    screen.blit(hud_text, (OFFSET_X, 15))

    # 4. Display & Clock
    pygame.display.flip()
    clock.tick(60)

pygame.quit()