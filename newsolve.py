import pygame
from collections import defaultdict

pygame.init()

# ----- SETTINGS -----
CELL = 40
ROWS, COLS = 9, 12
SCREEN = pygame.display.set_mode((COLS * CELL, ROWS * CELL))
pygame.display.set_caption("Line Follower Maze – Complex DFS L/S/R/B")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

TRACK_WIDTH = 8

# ----- MAZE DATA -----
start = (8, 1)
end = (1, 10)
bot_pos = start

# Main path
main_path = [
    (8,1),(7,1),(6,1),(5,1),(4,1),
    (3,1),(2,1),(1,1),(1,2),(1,3),(1,4),(1,5),
    (2,5),(3,5),(4,5),(5,5),(6,5),(6,6),(6,7),
    (5,7),(4,7),(3,7),(2,7),(1,7),(1,8),(1,9),(1,10)
]

# Branches: left/right branches, dead ends, loops
branches = [
    [(3,5),(3,3),(2,3)],            # left branch → dead end
    [(5,5),(5,3),(4,3),(4,4),(5,4)], # left branch → loop reconnects
    [(4,7),(4,9)],                   # right branch → dead end
    [(2,7),(2,6),(1,6)],             # left branch → dead end
    [(6,1),(6,3)],                   # right branch → dead end
    [(5,7),(7,7),(7,6),(6,6)],       # loop branch → reconnects main path
    [(3,1),(3,2),(2,2)],             # small left dead end
    [(1,3),(0,3)],                   # top left dead end
    [(1,5),(0,5)],                   # new top left branch
    [(6,7),(6,8),(5,8),(4,8)],       # right branch → dead end
]

# ----- GRAPH -----
graph = defaultdict(list)

def add_edge(a, b):
    if b not in graph[a]:
        graph[a].append(b)
    if a not in graph[b]:
        graph[b].append(a)

def register_path(path):
    for i in range(len(path) - 1):
        add_edge(path[i], path[i + 1])

register_path(main_path)
for b in branches:
    register_path(b)

# ----- DRAWING -----
def draw_line(points):
    for i in range(len(points) - 1):
        r1, c1 = points[i]
        r2, c2 = points[i + 1]
        x1, y1 = c1*CELL + CELL//2, r1*CELL + CELL//2
        x2, y2 = c2*CELL + CELL//2, r2*CELL + CELL//2
        pygame.draw.line(SCREEN, WHITE, (x1, y1), (x2, y2), TRACK_WIDTH)

def draw_maze(bot):
    SCREEN.fill(BLACK)
    draw_line(main_path)
    for b in branches:
        draw_line(b)
    font = pygame.font.SysFont(None, 28)
    SCREEN.blit(font.render("START", True, GREEN), (start[1]*CELL+5, start[0]*CELL+5))
    SCREEN.blit(font.render("END", True, GREEN), (end[1]*CELL+5, end[0]*CELL+5))
    pygame.draw.circle(SCREEN, BLUE, (bot[1]*CELL+CELL//2, bot[0]*CELL+CELL//2), TRACK_WIDTH)
    pygame.display.flip()

# ----- DFS / NODE LOGIC -----
def turn_priority(prev, current, neighbor):
    """
    0=LEFT, 1=STRAIGHT, 2=RIGHT, 3=BACK
    Corrected for grid (row increases downward)
    """
    if not prev:
        return 1  # starting node → straight

    # Vectors (flip row for correct grid)
    vx = current[1] - prev[1]
    vy = prev[0] - current[0]
    nx = neighbor[1] - current[1]
    ny = current[0] - neighbor[0]

    cp = vx*ny - vy*nx
    dp = vx*nx + vy*ny

    if cp > 0:
        return 0  # LEFT
    elif cp < 0:
        return 2  # RIGHT
    else:
        if dp > 0:
            return 1  # STRAIGHT
        else:
            return 3  # BACK

def detect_next_node(current, prev, visited_edges):
    neighbors = [n for n in graph[current] if frozenset([current,n]) not in visited_edges]
    if not neighbors:
        return prev  # dead end → backtrack
    neighbors.sort(key=lambda n: turn_priority(prev, current, n))
    next_node = neighbors[0]
    visited_edges.add(frozenset([current,next_node]))
    return next_node

# ----- MAIN LOOP -----
stack = [(start, None)]
visited_edges = set()

draw_maze(bot_pos)
pygame.time.wait(800)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if not stack:
        break

    node, prev = stack[-1]

    if node == end:
        bot_pos = node
        draw_maze(bot_pos)
        stack.pop()  # stop movement, but keep window open
        break

    next_node = detect_next_node(node, prev, visited_edges)

    if next_node == prev:  # backtrack
        stack.pop()
        if stack:
            bot_pos = stack[-1][0]
    else:
        stack.append((next_node, node))
        bot_pos = next_node

    draw_maze(bot_pos)

    # --- STEP-BY-STEP PAUSE ---
    print("Current Node:", node)
    print("Stack:", stack)
    print("Visited Edges:", visited_edges)
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = False

# ----- KEEP WINDOW OPEN UNTIL CLOSED -----
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.time.wait(50)









'''import pygame
from collections import defaultdict

pygame.init()

# ----- SETTINGS -----
CELL = 40
ROWS, COLS = 9, 12
SCREEN = pygame.display.set_mode((COLS * CELL, ROWS * CELL))
pygame.display.set_caption("Line Follower Maze – Iterative DFS L/S/R/B")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

TRACK_WIDTH = 8
SPEED = 500  # ms between bot moves

# ----- PATH DATA -----
start = (8, 1)
end = (1, 10)
bot_pos = start

# Main path: only 90° turns
main_path = [
    (8,1),(7,1),(6,1),(5,1),(4,1),
    (3,1),(2,1),(1,1),(1,2),(1,3),(1,4),(1,5),
    (2,5),(3,5),(4,5),(5,5),(6,5),(6,6),(6,7),
    (5,7),(4,7),(3,7),(2,7),(1,7),(1,8),(1,9),(1,10)
]

# Branches: including left branches
branches = [
    [(3,5),(3,3)],        # left branch
    [(5,5),(5,3)],
    [(4,7),(4,9)],
    [(2,7),(2,6)],        # left branch
    [(6,1),(6,3)],
    [(5,7),(7,7)],
    [(3,1),(3,2),(2,2)],
    [(4,5),(4,4),(5,4)],
    [(1,3),(0,3)],        # left branch at top
]

# ----- GRAPH -----
graph = defaultdict(list)

def add_edge(a, b):
    if b not in graph[a]:
        graph[a].append(b)
    if a not in graph[b]:
        graph[b].append(a)

def register_path(path):
    for i in range(len(path) - 1):
        add_edge(path[i], path[i + 1])

register_path(main_path)
for b in branches:
    register_path(b)

# ----- DRAWING -----
def draw_line(points):
    for i in range(len(points) - 1):
        r1, c1 = points[i]
        r2, c2 = points[i + 1]
        x1, y1 = c1*CELL + CELL//2, r1*CELL + CELL//2
        x2, y2 = c2*CELL + CELL//2, r2*CELL + CELL//2
        pygame.draw.line(SCREEN, WHITE, (x1, y1), (x2, y2), TRACK_WIDTH)

def draw_maze(bot):
    SCREEN.fill(BLACK)
    draw_line(main_path)
    for b in branches:
        draw_line(b)
    font = pygame.font.SysFont(None, 28)
    SCREEN.blit(font.render("START", True, GREEN), (start[1]*CELL+5, start[0]*CELL+5))
    SCREEN.blit(font.render("END", True, GREEN), (end[1]*CELL+5, end[0]*CELL+5))
    pygame.draw.circle(SCREEN, BLUE, (bot[1]*CELL+CELL//2, bot[0]*CELL+CELL//2), TRACK_WIDTH)
    pygame.display.flip()

# ----- DFS / NODE LOGIC -----
def is_junction(node):
    return len(graph[node]) > 2

def turn_priority(prev, current, neighbor):
    """
    0=LEFT, 1=STRAIGHT, 2=RIGHT, 3=BACK
    Cross-product fixed for grid coordinates (row increases downward)
    """
    if not prev:
        return 1  # starting node → straight

    # Vectors (flip row component)
    vx = current[1] - prev[1]       # column difference
    vy = prev[0] - current[0]       # row difference flipped
    nx = neighbor[1] - current[1]
    ny = current[0] - neighbor[0]   # row difference flipped

    cp = vx*ny - vy*nx
    dp = vx*nx + vy*ny

    if cp > 0:
        return 0  # LEFT
    elif cp < 0:
        return 2  # RIGHT
    else:
        if dp > 0:
            return 1  # STRAIGHT
        else:
            return 3  # BACK


def detect_next_node(current, prev, visited_edges):
    neighbors = [n for n in graph[current] if frozenset([current,n]) not in visited_edges]
    if not neighbors:
        return prev  # dead end → backtrack

    # Sort neighbors by L/S/R/B priority
    neighbors.sort(key=lambda n: turn_priority(prev, current, n))
    next_node = neighbors[0]
    visited_edges.add(frozenset([current,next_node]))
    return next_node

# ----- MAIN LOOP -----
stack = [(start, None)]
visited_edges = set()

draw_maze(bot_pos)
pygame.time.wait(800)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not stack:
        break

    node, prev = stack[-1]

    if node == end:
        bot_pos = node
        draw_maze(bot_pos)
        break

    next_node = detect_next_node(node, prev, visited_edges)

    if next_node == prev:  # backtrack
        stack.pop()
        if stack:
            bot_pos = stack[-1][0]
    else:
        stack.append((next_node, node))
        bot_pos = next_node

    draw_maze(bot_pos)
    pygame.time.wait(SPEED)

pygame.time.wait(1500)
pygame.quit()
'''