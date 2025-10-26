import json
import numpy as np
import cv2 as cv
from command import Command


def generate_toolpath(img: np.ndarray) -> list[Command]:
    # img_int = img.astype(np.uint8)
    # img = img_int
    img = add_border(img)
    # white_pixel_count = np.sum(img_int == 1)
    # print(white_pixel_count)
    print(img)
    commands = []

    current_point = (0, 0)
    white_pixel_count = np.sum(img == 255)
    print(white_pixel_count)
    # exit()
    while white_pixel_count > 0:
        prev_point = current_point
        point, img = find_next_point(img, white_pixel_count, current_point)

        next_point_commands, img = gen_path_to_next_point(prev_point, point, img)
        print(next_point_commands)
        commands = commands + next_point_commands
        white_pixel_count -= 1

        adjacent, direction = cross_x_search(point, img)
        print(direction)
        if adjacent:
            command, current_point, img = gen_line_command(direction, point, img)

            print(repr(command))
            commands.append(command)
            white_pixel_count -= command.steps

    return commands


def gen_path_to_next_point(
    current_point: tuple[int, int], next_point: tuple[int, int], img: np.ndarray
) -> tuple[list[Command], np.ndarray]:
    # TODO add setting vals to 1
    commands = []
    y_command_steps = next_point[0] - current_point[0]
    y_direction = (1, 0)
    if y_command_steps < 0:
        y_command_steps = abs(y_command_steps)
        y_direction = (-1, 0)

    x_command_steps = next_point[1] - current_point[1]
    x_direction = (0, 1)
    if x_command_steps < 0:
        x_command_steps = abs(x_command_steps)
        x_direction = (0, -1)

    x_command = Command(x_direction[1], x_direction[0], x_command_steps)
    y_command = Command(y_direction[1], y_direction[0], y_command_steps)

    if x_command_steps > 0:
        commands.append(x_command)
    if y_command_steps > 0:
        commands.append(y_command)
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
    img: np.ndarray, total_white: int, origin: tuple[int, int] = (0, 0)
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

    while total_white > 0 or x > 5 * max(width, height):
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

    coms = generate_toolpath(image.canny("images/cat.jpg"))
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
