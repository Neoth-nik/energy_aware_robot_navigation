import pygame
from maze import (
    WIDTH, HEIGHT, ROWS, COLS, OFFSET_X, BG_COLOR, TEXT_COLOR,
    PrimMazeGenerator
)
from pathfinding import BFSPathfinder

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Energy-Aware Robot Navigation Visualizer")
font = pygame.font.SysFont("Consolas", 16, bold=True)

# Instantiate generator & pathfinder
maze_gen = PrimMazeGenerator(ROWS, COLS)
pathfinder = BFSPathfinder(maze_gen)
clock = pygame.time.Clock()

running = True

while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                # Clear previous search state & generate fresh maze
                pathfinder.reset()
                maze_gen.start_generation(start_row=0, start_col=0)

            elif event.key == pygame.K_r:
                pathfinder.reset()
                maze_gen.reset()

            elif event.key == pygame.K_s:
                # Trigger BFS pathfinder only when maze isn't generating
                if not maze_gen.is_generating:
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    pathfinder.start_search(start_cell, goal_cell)

    # 2. Algorithm Step Updates (Animation)
    if maze_gen.is_generating:
        maze_gen.step()
        maze_gen.step()
    elif pathfinder.is_searching:
        pathfinder.step()
        pathfinder.step()  # Step twice per frame for faster visualization

    # 3. Render Graphics
    screen.fill(BG_COLOR)
    maze_gen.draw(screen)

    # Status Banner
    if maze_gen.is_generating:
        status = "STATUS: GENERATING MAZE..."
    elif pathfinder.is_searching:
        status = "STATUS: RUNNING BFS..."
    elif pathfinder.found_path:
        status = "STATUS: PATH FOUND!"
    else:
        status = "STATUS: IDLE"

    hud_text = font.render(f"[G] Generate | [S] BFS Pathfind | [R] Reset | {status}", True, TEXT_COLOR)
    screen.blit(hud_text, (OFFSET_X, 15))

    # 4. Display & Clock
    pygame.display.flip()
    clock.tick(60)

pygame.quit()