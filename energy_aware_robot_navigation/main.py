import pygame
from maze import (
    WIDTH, HEIGHT, ROWS, COLS, OFFSET_X, BG_COLOR, TEXT_COLOR,
    PrimMazeGenerator
)

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Energy-Aware Robot Navigation Visualizer")
font = pygame.font.SysFont("Consolas", 16, bold=True)

# Instantiate generator
maze_gen = PrimMazeGenerator(ROWS, COLS)
clock = pygame.time.Clock()

running = True

while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                maze_gen.start_generation(start_row=0, start_col=0)

            elif event.key == pygame.K_r:
                maze_gen.reset()

    # 2. Algorithm Step Update
    if maze_gen.is_generating:
        maze_gen.step()
        maze_gen.step()

    # 3. Render Graphics
    screen.fill(BG_COLOR)
    maze_gen.draw(screen)

    status = "STATUS: GENERATING MAZE..." if maze_gen.is_generating else "STATUS: IDLE"
    hud_text = font.render(f"[G] Generate | [R] Reset | {status}", True, TEXT_COLOR)
    screen.blit(hud_text, (OFFSET_X, 15))

    # 4. Display & Clock
    pygame.display.flip()
    clock.tick(60)

pygame.quit()