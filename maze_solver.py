import pygame
from collections import defaultdict

pygame.init()

# ----- SETTINGS -----
CELL = 40
ROWS, COLS = 9, 12
SCREEN = pygame.display.set_mode((COLS * CELL, ROWS * CELL))
pygame.display.set_caption("Line Follower Maze – DFS (R S L B)")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

TRACK_WIDTH = 8
SPEED = 500 # milliseconds between bot moves

# ----- PATH DATA -----
start = (8, 1)
end = (1, 10)
bot_pos = start

main_path = [
    (8,1),(7,1),(6,1),(5,1),(4,1),
    (3,1),(2,1),(1,1),(1,3),(1,5),
    (2,5),(3,5),(4,5),(5,5),(6,5),
    (6,7),(5,7),(4,7),(3,7),(2,8),
    (1,8),(1,10)
]

branches = [
    [(3,5),(3,3)],
    [(5,5),(5,3)],
    [(4,7),(4,9)],
    [(2,8),(2,10)],
    [(6,1),(6,3)],
    [(5,7),(7,7)],
    [(3,1),(3,2),(2,2)],
    [(4,5),(4,4),(5,4)],
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

# ----- PRIORITY SORT (R > S > L > B) -----
def priority_sort(current, prev, neighbors):
    if not prev:
        return neighbors

    dr = current[0] - prev[0]
    dc = current[1] - prev[1]
    heading = (dr, dc)

    def rel_priority(n):
        vec = (n[0] - current[0], n[1] - current[1])
        # For each heading: [Right, Straight, Left, Back]
        if heading == (0, 1):      # facing East
            order = [(1,0),(0,1),(-1,0),(0,-1)]
        elif heading == (1, 0):    # facing South
            order = [(0,-1),(1,0),(0,1),(-1,0)]
        elif heading == (0, -1):   # facing West
            order = [(-1,0),(0,-1),(1,0),(0,1)]
        else:                      # facing North
            order = [(0,1),(-1,0),(0,-1),(1,0)]
        return order.index(vec) if vec in order else 99

    return sorted(neighbors, key=rel_priority)

# ----- DRAWING -----
def draw_line(points):
    for i in range(len(points) - 1):
        r1, c1 = points[i]
        r2, c2 = points[i + 1]
        x1, y1 = c1 * CELL + CELL // 2, r1 * CELL + CELL // 2
        x2, y2 = c2 * CELL + CELL // 2, r2 * CELL + CELL // 2
        pygame.draw.line(SCREEN, WHITE, (x1, y1), (x2, y2), TRACK_WIDTH)

def draw_maze(bot):
    SCREEN.fill(BLACK)
    draw_line(main_path)
    for b in branches:
        draw_line(b)

    font = pygame.font.SysFont(None, 28)
    SCREEN.blit(font.render("START", True, GREEN),
                (start[1]*CELL + 5, start[0]*CELL + 5))
    SCREEN.blit(font.render("END", True, GREEN),
                (end[1]*CELL + 5, end[0]*CELL + 5))

    pygame.draw.circle(SCREEN, BLUE,
                       (bot[1]*CELL + CELL//2, bot[0]*CELL + CELL//2),
                       TRACK_WIDTH)
    pygame.display.flip()

# ----- DFS SEARCH LOOP -----
stack = [(start, None)]
visited_edges = set()

draw_maze(bot_pos)
pygame.time.wait(800)  # short pause before starting

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

    # Pick neighbor with R>S>L>B
    nbrs = priority_sort(node, prev, graph[node])
    next_node = None
    for nb in nbrs:
        edge = tuple(sorted([node, nb]))
        if edge not in visited_edges:
            visited_edges.add(edge)
            next_node = nb
            break

    if next_node:
        stack.append((next_node, node))
        bot_pos = next_node
    else:
        stack.pop()
        if stack:
            bot_pos = stack[-1][0]

    draw_maze(bot_pos)
    pygame.time.wait(SPEED)   # smoother than time.sleep()

pygame.time.wait(1500)
pygame.quit()
