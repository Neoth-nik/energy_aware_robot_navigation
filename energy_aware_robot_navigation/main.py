import pygame
from maze import (
    WIDTH, HEIGHT, ROWS, COLS, OFFSET_X, BG_COLOR, TEXT_COLOR,
    PrimMazeGenerator
)
from pathfinding import BFSPathfinder, AStarPathfinder
from robot import Robot

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Energy-Aware Robot Navigation Visualizer")
font = pygame.font.SysFont("Consolas", 15, bold=True)

# Instantiate maze generator, pathfinders, and robot object
maze_gen = PrimMazeGenerator(ROWS, COLS)
bfs_solver = BFSPathfinder(maze_gen)
astar_solver = AStarPathfinder(maze_gen)
robot = Robot(start_row=0, start_col=0, max_energy=500.0)

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
                robot.reset()
                active_solver = None
                maze_gen.start_generation(start_row=0, start_col=0)

            elif event.key == pygame.K_r:
                bfs_solver.reset()
                astar_solver.reset()
                robot.reset()
                active_solver = None
                maze_gen.reset()

            elif event.key == pygame.K_b:
                if not maze_gen.is_generating:
                    bfs_solver.reset()
                    astar_solver.reset()
                    robot.reset()
                    active_solver = bfs_solver
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    bfs_solver.start_search(start_cell, goal_cell)

            elif event.key == pygame.K_a:
                if not maze_gen.is_generating:
                    bfs_solver.reset()
                    astar_solver.reset()
                    robot.reset()
                    active_solver = astar_solver
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    astar_solver.start_search(start_cell, goal_cell)

    # 2. Algorithm & Robot Motion Updates
    if maze_gen.is_generating:
        maze_gen.step()
        maze_gen.step()
    elif active_solver and active_solver.is_searching:
        active_solver.step()
        active_solver.step()
        # Transfer path to robot upon pathfinding completion
        if active_solver.found_path and not robot.is_moving and not robot.path:
            path_nodes = active_solver._reconstruct_path()
            robot.set_path(path_nodes)
            
    # Update robot state (position lerping & energy tracking)
    robot.update(speed=0.20)

    # 3. Render Graphics
    screen.fill(BG_COLOR)
    maze_gen.draw(screen)
    
    # Draw Robot on top of grid
    robot.draw(screen)

    # Status & HUD Banner
    if maze_gen.is_generating:
        status = "GENERATING MAZE..."
    elif active_solver and active_solver.is_searching:
        solver_name = "BFS" if active_solver == bfs_solver else "A*"
        status = f"RUNNING {solver_name}..."
    elif robot.is_moving:
        status = "ROBOT NAVIGATING..."
    elif active_solver and active_solver.found_path:
        status = "NAVIGATION COMPLETE!"
    else:
        status = "IDLE"

    hud_text = font.render(
        f"[G] Gen | [B] BFS | [A] A* | [R] Reset | {status}",
        True, TEXT_COLOR
    )
    energy_text = font.render(
        f"Robot Energy Consumed: {robot.energy_consumed:.1f} units | Facing: {robot.heading}",
        True, (241, 196, 15)
    )
    
    screen.blit(hud_text, (OFFSET_X, 10))
    screen.blit(energy_text, (OFFSET_X, 30))

    # 4. Display & Clock
    pygame.display.flip()
    clock.tick(60)

pygame.quit()