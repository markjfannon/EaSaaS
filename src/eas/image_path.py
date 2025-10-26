import image
import json
import numpy as np
import math
from sys import argv
from command import Command

visited_pixels: set[tuple[int, int]] = set()


def sign(x: int) -> int:
    return int(math.copysign(1, x)) if x != 0 else 0


# yields offsets in a spiral pattern, uses (y, x)
def generate_spiral_offsets():
    radius = 1
    directions = [
        (0, 1),
        (1, 0),
        (0, -1),
        (-1, 0),
    ]

    while True:
        current_x = -radius
        current_y = -radius
        for dir_y, dir_x in directions:
            while True:
                yield (current_y, current_x)
                current_x += dir_x
                current_y += dir_y

                if abs(current_x) == radius and abs(current_y) == radius:
                    # Go to next direction
                    break

        radius += 1


def spiral_search(image: np.ndarray, origin: tuple[int, int]) -> tuple[int, int]:
    origin_y, origin_x = origin
    height, width = image.shape

    for i, (offset_y, offset_x) in enumerate(generate_spiral_offsets()):
        current_y = origin_y + offset_y
        current_x = origin_x + offset_x
        current_pos = (current_y, current_x)

        # Discard out of bounds
        if current_y < 0 or current_y >= height or current_x < 0 or current_x >= width:
            continue

        # Discard black pixels
        if image[current_y, current_x] != 255:
            continue

        # Discard visited pixels
        if current_pos in visited_pixels:
            continue

        return current_pos


def cross_x_search(
    image: np.ndarray, origin: tuple[int, int]
) -> tuple[int, int] | None:
    check_offsets = [
        (0, 1),
        (0, -1),
        (1, 0),
        (-1, 0),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    ]

    origin_y, origin_x = origin
    height, width = image.shape

    for offset_y, offset_x in check_offsets:
        current_y = origin_y + offset_y
        current_x = origin_x + offset_x
        current_pos = (current_y, current_x)

        # Discard out of bounds
        if current_y < 0 or current_y >= height or current_x < 0 or current_x >= width:
            continue

        # Discard black pixels
        if image[current_y, current_x] != 255:
            continue

        # Discard visited pixels
        if current_pos in visited_pixels:
            continue

        return current_pos

    return None


def traverse_to_point(
    start_point: tuple[int, int], end_point: tuple[int, int]
) -> list[Command]:
    commands = []

    start_point_y, start_point_x = start_point
    end_point_y, end_point_x = end_point

    x_dist = end_point_x - start_point_x
    y_dist = end_point_y - start_point_y

    diagonal_dist = min(abs(x_dist), abs(y_dist))
    y_dir = sign(y_dist)
    x_dir = sign(x_dist)

    commands.append(Command(x=x_dir, y=y_dir, steps=diagonal_dist))

    if diagonal_dist > 0 and 2 * diagonal_dist < abs(x_dist) + abs(y_dist):
        current_x = start_point_x + diagonal_dist * x_dir
        current_y = start_point_y + diagonal_dist * y_dir
        dist = abs(end_point_x - current_x) + abs(end_point_y - current_y)

        commands.append(
            Command(
                x=sign(end_point_x - current_x),
                y=sign(end_point_y - current_y),
                steps=dist,
            )
        )

    return commands


def generate_path(image: np.ndarray) -> list[Command]:
    commands = []
    num_whites = np.sum(image == 255)
    print(num_whites)

    current_pos = (0, 0)
    while len(visited_pixels) < num_whites:
        found_point = spiral_search(image, current_pos)

        commands.extend(traverse_to_point(current_pos, found_point))
        current_pos = found_point
        visited_pixels.add(current_pos)

        while True:
            next_point = cross_x_search(image, current_pos)
            if next_point is None:
                break

            commands.extend(traverse_to_point(current_pos, next_point))
            current_pos = next_point
            visited_pixels.add(current_pos)

    return commands


def main():
    if len(argv) != 2:
        print("Nuh uh! Supply a single argument please")
        return

    coms = generate_path(image.canny(argv[1]))

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
            # print(f"x: {com.x}, y: {com.y}, steps: {com.steps * STEPS_PER_PIXEL}")


if __name__ == "__main__":
    main()
