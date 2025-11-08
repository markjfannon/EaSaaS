import json
import numpy as np
from collections import deque
from command import Command
from constants import DIRECTIONS


def generate_toolpath(img: np.ndarray) -> list[Command]:
    # img = add_border(img)
    print(img)
    commands = []

    current_point = (0, 0)
    # exit()
    while np.any(img == 255):
        prev_point = current_point
        point, img = find_next_point(img, current_point)

        next_point_commands, img = gen_path_to_next_point(prev_point, point, img)
        commands = commands + next_point_commands

        current_point = point
        adjacent, direction = cross_x_search(current_point, img)
        while adjacent:
            command, current_point, img = gen_line_command(
                direction, current_point, img
            )

            commands.append(command)

            adjacent, direction = cross_x_search(current_point, img)

    return commands


def gen_path_to_next_point(
    current_point: tuple[int, int], next_point: tuple[int, int], img: np.ndarray
) -> tuple[list[Command], np.ndarray]:
    """
    Moves from current_point to next_point in two phases:
    1. Follows existing drawn pixels (value 1) to get as close as possible.
    2. Draws a new line (diagonal + straight) to reach the target,
       marking traversed pixels as 1.
    """
    commands = []
    height, width = img.shape

    # follow existing path

    queue = deque([current_point])
    visited_bfs: set[tuple[int, int]] = {current_point}
    parent_map: dict[tuple[int, int], tuple[int, int]] = {current_point: None}

    closest_pos_on_path = current_point
    min_dist_sq = (next_point[0] - current_point[0]) ** 2 + (
        next_point[1] - current_point[1]
    ) ** 2

    while queue:
        y, x = queue.popleft()

        # Check if this point is closer to the target
        dist_sq = (next_point[0] - y) ** 2 + (next_point[1] - x) ** 2
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            closest_pos_on_path = (y, x)

        # Explore neighbors
        for dy, dx in DIRECTIONS:
            ny, nx = y + dy, x + dx
            neighbor = (ny, nx)

            # Check if we've seen it in this BFS, and if it's a '1' pixel
            if (
                0 <= ny < height
                and 0 <= nx < width
                and neighbor not in visited_bfs
                and img[ny, nx] == 1
            ):  # Only follow existing path
                visited_bfs.add(neighbor)
                parent_map[neighbor] = (y, x)
                queue.append(neighbor)

    # reconstruct path
    path: list[tuple[int, int]] = []
    curr = closest_pos_on_path
    while curr is not None:
        path.append(curr)
        curr = parent_map.get(curr)
    path.reverse()  # Path is now [current_pos, step1, ..., closest_pos_on_path]

    # Convert path into commands
    i = 0
    while i < len(path) - 1:
        p_start = path[i]
        p_next = path[i + 1]

        dy, dx = p_next[0] - p_start[0], p_next[1] - p_start[1]
        steps = 0

        # Look ahead to see how long we move in this direction
        j = i
        while j < len(path) - 1:
            step_dy = path[j + 1][0] - path[j][0]
            step_dx = path[j + 1][1] - path[j][1]

            if (step_dy, step_dx) == (dy, dx):
                steps += 1
                j += 1
            else:
                break

        if steps > 0:
            commands.append(Command(x=dx, y=dy, steps=steps))

        i = j

    # Update current_point to where this path-following ended
    current_point = closest_pos_on_path

    # After BFS, draw new lines
    if current_point == next_point:
        return commands, img  # We're already there

    # Calculate direction for diagonal move
    dy = next_point[0] - current_point[0]
    dx = next_point[1] - current_point[1]

    dir_y = 1 if dy > 0 else -1 if dy < 0 else 0
    dir_x = 1 if dx > 0 else -1 if dx < 0 else 0

    # Diagonal Command
    diag_steps = min(abs(dy), abs(dx))
    if diag_steps > 0:
        commands.append(Command(x=dir_x, y=dir_y, steps=diag_steps))
        # Mark traveled pixels as '1'
        for i in range(1, diag_steps + 1):
            img[current_point[0] + (dir_y * i), current_point[1] + (dir_x * i)] = 1

        # Update current_pos
        current_point = (
            current_point[0] + (dir_y * diag_steps),
            current_point[1] + (dir_x * diag_steps),
        )

    # Adjustment Command
    dy_adj = next_point[0] - current_point[0]
    dx_adj = next_point[1] - current_point[1]

    adj_steps = max(abs(dy_adj), abs(dx_adj))
    if adj_steps > 0:
        adj_dir_y = 1 if dy_adj > 0 else -1 if dy_adj < 0 else 0
        adj_dir_x = 1 if dx_adj > 0 else -1 if dx_adj < 0 else 0
        commands.append(Command(x=adj_dir_x, y=adj_dir_y, steps=adj_steps))

        # Mark traveled pixels as '1'
        for i in range(1, adj_steps + 1):
            img[
                current_point[0] + (adj_dir_y * i), current_point[1] + (adj_dir_x * i)
            ] = 1

    return commands, img


def add_border(img: np.ndarray) -> np.ndarray:
    height, width = img.shape

    img[0, :] = 1
    img[height - 1, :] = 1
    img[:, 0] = 1
    img[:, width - 1] = 1

    return img


def cross_x_search(
    point: tuple[int, int], img: np.ndarray
) -> tuple[bool, tuple[int, int]]:
    """
    Returns found_bool, direction,
    """
    check_order = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for to_check in check_order:
        current_point = (point[0] + to_check[0], point[1] + to_check[1])
        if img[current_point[0], current_point[1]] >= 255:
            return True, to_check

    return False, (0, 0)


def gen_line_command(
    direction: tuple[int, int], point: tuple[int, int], img: np.ndarray
) -> tuple[Command, tuple[int, int], np.ndarray]:
    """
    Remember to lower white_pixel_cound by num of steps in command
    """
    step_count = 0
    prev_point = point
    next_point = (point[0] + direction[0], point[1] + direction[1])
    while img[next_point] == 255:
        step_count += 1
        img[next_point] = 1
        prev_point = next_point
        next_point = (next_point[0] + direction[0], next_point[1] + direction[1])

    return Command(x=direction[1], y=direction[0], steps=step_count), prev_point, img


def find_next_point(
    img: np.ndarray, origin: tuple[int, int] = (0, 0)
) -> tuple[tuple[int, int], np.ndarray]:
    height, width = img.shape
    # print(img.shape)

    x, y = origin
    dx, dy = 1, 0
    steps_to_take = 1
    steps_taken = 0
    turns = 0

    WHITE = 255
    FOUND = 1

    while np.any(img == 255) > 0 or x > 5 * max(width, height):
        # print(total_white)
        # print(img[y,x])

        if x >= 0 and x < width and y >= 0 and y < height and img[y, x] >= WHITE:
            img[y, x] = FOUND
            print(f"found white at ({x}, {y})")
            return (y, x), img

        x += dx
        y += dy
        steps_taken += 1

        if steps_taken == steps_to_take:
            steps_taken = 0

            dx, dy = -dy, dx

            turns += 1

            if turns % 2 == 0:
                steps_to_take += 1

    raise ValueError


if __name__ == "__main__":
    import image

    coms = generate_toolpath(image.canny("images/cat_lines.jpg"))
    with open("cat.jsonl", "w") as file:
        file.write('{"steps": 8192, "x_dir": 1, "y_dir": 1}\n')

        for com in coms:
            STEPS_PER_PIXEL = 100
            inst = {
                "steps": abs(com.steps) * STEPS_PER_PIXEL,
                "x_dir": com.x,
                "y_dir": com.y,
            }
            file.write(f"{json.dumps(inst)}\n")
            print(f"x: {com.x}, y: {com.y}, steps: {com.steps}")
        print(f"Length: {len(coms)}")
