import random

stepsToTake = 9

WORLD_WIDTH = 19
WORLD_HEIGHT = 9

def agentMoving(steps):
    # create empty world
    world = [['~' for _ in range(WORLD_WIDTH)] for _ in range(WORLD_HEIGHT)]

    # start from center
    x = WORLD_WIDTH // 2
    y = WORLD_HEIGHT // 2
    world[y][x] = '#'

    directions = [
        (0, -1),  # up
        (0, 1),   # down
        (1, 0),   # right
        (-1, 0)   # left
    ]

    # we already marked the starting cell, so do steps-1 more moves
    for _ in range(steps - 1):
        dx, dy = random.choice(directions)
        nx = x + dx
        ny = y + dy

        # keep the agent inside the world
        if 0 <= nx < WORLD_WIDTH and 0 <= ny < WORLD_HEIGHT:
            x, y = nx, ny

        world[y][x] = '#'

    # print the world
    for row in world:
        print(''.join(row))

if __name__ == "__main__":
    agentMoving(stepsToTake)
