import pygame
from pathfinding import FloodFillExplorer, BFSPathfinder, AStarPathfinder
from maze import (
    WIDTH, HEIGHT, ROWS, COLS, BG_COLOR, TEXT_COLOR,
    PANEL_W, PANEL_BG, PANEL_CARD, PANEL_BORDER, ACCENT,
    IN_MAZE_COLOR, START_COLOR, END_COLOR, PATH_COLOR, VISITED_COLOR,
    CURRENT_COLOR, FRONTIER_COLOR,
    PrimMazeGenerator
)
from robot import Robot

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Navigation Visualizer")

title_font = pygame.font.SysFont("Consolas", 22, bold=True)
font = pygame.font.SysFont("Consolas", 15, bold=True)
small_font = pygame.font.SysFont("Consolas", 13)

maze_gen = PrimMazeGenerator(ROWS, COLS)
robot = Robot(start_row=0, start_col=0)
explorer = FloodFillExplorer(maze_gen)
bfs_solver = BFSPathfinder(maze_gen)
astar_solver = AStarPathfinder(maze_gen)
active_solver = None

# mode: 'idle' | 'exploring' | 'explore_done' | 'fast_run'
#       | 'bfs_solving' | 'astar_solving' | 'finished'
mode = 'idle'
run_label = ""              # which algorithm produced the last/current run
path_dispatched = False     # has the solver's path been given to the robot?

# Stats
steps = 0
explore_steps = None
last_pos = (0, 0)
run_start_ms = None
run_end_ms = None

clock = pygame.time.Clock()
running = True


def start_timer():
    global run_start_ms, run_end_ms
    run_start_ms = pygame.time.get_ticks()
    run_end_ms = None


def full_reset():
    global explorer, mode, active_solver, path_dispatched
    global steps, explore_steps, last_pos, run_start_ms, run_end_ms, run_label
    robot.reset()
    explorer = FloodFillExplorer(maze_gen)
    bfs_solver.reset()
    astar_solver.reset()
    active_solver = None
    mode = 'idle'
    run_label = ""
    path_dispatched = False
    steps = 0
    explore_steps = None
    last_pos = (0, 0)
    run_start_ms = None
    run_end_ms = None

# UI helpers
def draw_card(x, y, w, h):
    pygame.draw.rect(screen, PANEL_CARD, (x, y, w, h), border_radius=8)


def draw_section_title(text, x, y):
    surf = small_font.render(text, True, ACCENT)
    screen.blit(surf, (x, y))
    pygame.draw.line(screen, PANEL_BORDER, (x, y + 20), (PANEL_W - 20, y + 20), 1)
    return y + 30


def draw_key(key, label, x, y):
    badge = pygame.Rect(x, y, 26, 24)
    pygame.draw.rect(screen, (60, 66, 84), badge, border_radius=5)
    k = font.render(key, True, (255, 255, 255))
    screen.blit(k, k.get_rect(center=badge.center))
    screen.blit(font.render(label, True, TEXT_COLOR), (x + 38, y + 3))


def draw_stat(label, value, x, y):
    screen.blit(small_font.render(label, True, (140, 150, 170)), (x, y))
    v = font.render(str(value), True, (255, 255, 255))
    screen.blit(v, (PANEL_W - 30 - v.get_width(), y - 2))


def draw_legend_item(color, label, x, y):
    pygame.draw.rect(screen, color, (x, y, 16, 16), border_radius=3)
    screen.blit(small_font.render(label, True, TEXT_COLOR), (x + 24, y + 1))


def get_status():
    if maze_gen.is_generating:
        return "GENERATING MAZE", FRONTIER_COLOR
    if mode == 'exploring':
        return "EXPLORING (mapping walls)", CURRENT_COLOR
    if mode == 'explore_done':
        return "EXPLORATION DONE", START_COLOR
    if mode == 'fast_run':
        return "FAST RUN (using own map)", PATH_COLOR
    if mode == 'bfs_solving':
        return "RUNNING BFS", VISITED_COLOR
    if mode == 'astar_solving':
        return "RUNNING A*", VISITED_COLOR
    if mode == 'finished':
        return f"{run_label} COMPLETE!", START_COLOR
    return "IDLE", (150, 155, 170)


def draw_panel():
    pygame.draw.rect(screen, PANEL_BG, (0, 0, PANEL_W, HEIGHT))
    pygame.draw.line(screen, PANEL_BORDER, (PANEL_W, 0), (PANEL_W, HEIGHT), 2)

    x = 20
    y = 20
    screen.blit(title_font.render("ROBOT NAVIGATION", True, (255, 255, 255)), (x, y))
    screen.blit(small_font.render("Maze solving visualizer", True, (140, 150, 170)), (x, y + 28))
    y += 62

    # Status card
    draw_card(x, y, PANEL_W - 40, 54)
    status_text, status_color = get_status()
    pygame.draw.circle(screen, status_color, (x + 20, y + 27), 7)
    screen.blit(small_font.render("STATUS", True, (140, 150, 170)), (x + 38, y + 8))
    screen.blit(font.render(status_text, True, (255, 255, 255)), (x + 38, y + 27))
    y += 74

    # Controls
    y = draw_section_title("CONTROLS", x, y)
    for key, label in [("G", "Generate maze"), ("E", "Micromouse explore"),
                       ("B", "Solve with BFS"), ("A", "Solve with A*"),
                       ("R", "Reset / clear")]:
        draw_key(key, label, x, y)
        y += 32
    y += 10

    # Statistics
    y = draw_section_title("STATISTICS", x, y)
    explored = sum(1 for r in maze_gen.grid for c in r if c.is_visited)
    path_len = sum(1 for r in maze_gen.grid for c in r if c.is_path)
    if run_start_ms is None:
        elapsed = "--"
    else:
        end = run_end_ms if run_end_ms is not None else pygame.time.get_ticks()
        elapsed = f"{(end - run_start_ms) / 1000:.1f}s"

    stats = [("Maze size", f"{ROWS} x {COLS}"),
             ("Cells explored", explored),
             ("Path length", path_len if path_len else "--")]
    if explore_steps is not None:
        stats.append(("Exploration steps", explore_steps))
        stats.append(("Fast-run steps", steps))
    else:
        stats.append(("Robot steps", steps))
    stats.append(("Elapsed time", elapsed))
    stats.append(("Heading", robot.heading))
    for label, value in stats:
        draw_stat(label, value, x, y)
        y += 26
    y += 10

    # Legend
    y = draw_section_title("LEGEND", x, y)
    items = [(START_COLOR, "Start"), (END_COLOR, "Goal"),
             (PATH_COLOR, "Final path"), (VISITED_COLOR, "Visited"),
             (CURRENT_COLOR, "Current cell"), (FRONTIER_COLOR, "Frontier"),
             (IN_MAZE_COLOR, "Open passage")]
    col_w = (PANEL_W - 40) // 2
    for i, (color, label) in enumerate(items):
        draw_legend_item(color, label, x + (i % 2) * col_w, y + (i // 2) * 26)


# Main loop
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
                    full_reset()
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    explorer.start_exploration(start_cell, goal_cell)
                    run_label = "MICROMOUSE"
                    mode = 'exploring'
                    start_timer()

            elif event.key == pygame.K_b:
                if not maze_gen.is_generating:
                    full_reset()
                    active_solver = bfs_solver
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    bfs_solver.start_search(start_cell, goal_cell)
                    run_label = "BFS"
                    mode = 'bfs_solving'
                    start_timer()

            elif event.key == pygame.K_a:
                if not maze_gen.is_generating:
                    full_reset()
                    active_solver = astar_solver
                    start_cell = maze_gen.grid[0][0]
                    goal_cell = maze_gen.grid[ROWS - 1][COLS - 1]
                    astar_solver.start_search(start_cell, goal_cell)
                    run_label = "A*"
                    mode = 'astar_solving'
                    start_timer()

    # 2. Simulation Update
    if maze_gen.is_generating:
        maze_gen.step()
        maze_gen.step()

    elif mode == 'exploring':
        if not robot.is_moving:
            explorer.current_cell = maze_gen.grid[robot.row][robot.col]
            next_cell = explorer.advance(robot.heading)
            if next_cell is not None:
                robot.set_path([next_cell])
            else:
                mode = 'explore_done'

    elif mode in ('bfs_solving', 'astar_solving'):
        if active_solver.is_searching:
            active_solver.step()
            active_solver.step()
        elif active_solver.found_path and not path_dispatched:
            robot.set_path(active_solver._reconstruct_path())
            path_dispatched = True
        elif not robot.is_moving:
            mode = 'finished'
            run_end_ms = pygame.time.get_ticks()

    elif mode == 'explore_done':
        explore_steps = steps
        steps = 0
        fastest_path = explorer.solve_fastest_known_path()
        robot.reset(start_row=0, start_col=0)
        last_pos = (0, 0)
        if fastest_path:
            robot.set_path(fastest_path)
        mode = 'fast_run'

    elif mode == 'fast_run':
        if not robot.is_moving:
            mode = 'finished'
            run_end_ms = pygame.time.get_ticks()

    # Exploration is slower, everything else is snappier
    robot.update(speed=0.30 if mode == 'exploring' else 0.40)

    # Count a step every time the robot enters a new cell
    if (robot.row, robot.col) != last_pos:
        steps += 1
        last_pos = (robot.row, robot.col)

    # 3. Render Graphics
    screen.fill(BG_COLOR)
    maze_gen.draw(screen)
    robot.draw(screen)
    draw_panel()

    # 4. Display & Clock
    pygame.display.flip()
    clock.tick(60)

pygame.quit()