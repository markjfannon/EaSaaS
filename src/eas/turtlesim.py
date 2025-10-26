from turtle import Turtle
from constants import SCREEN_HEIGHT_MM, SCREEN_WIDTH_MM
from command import Command
import json
from sys import argv

t = Turtle()

STEPS_PER_MM = 50


def load_file(filename: str) -> list[Command]:
    commands = []
    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:
            inst = json.loads(line)
            commands.append(
                Command(x=inst["x_dir"], y=inst["y_dir"], steps=inst["steps"])
            )

    return commands


def main():
    if len(argv) != 2:
        print("Nuh uh! Supply a single argument please")
        return

    commands = load_file(argv[1])

    setup_turtle()
    draw_commands(commands)

    t.screen.mainloop()


def setup_turtle():
    t.screen.title("Etch-a-Sketch Simulator")
    t.screen.tracer(8)
    t.hideturtle()
    t.penup()
    set_position(0, 0)
    t.pendown()
    # eas_width = (7 * 4096) / STEPS_PER_MM
    # eas_height = (7 * 4096) / STEPS_PER_MM
    # set_position(eas_width, 0)
    # set_position(eas_width, eas_height)
    # set_position(0, eas_height)
    # set_position(0, 0)


def draw_commands(commands: list[Command]):
    current_x = 0
    current_y = 0
    for command in commands:
        current_x += (command.steps / STEPS_PER_MM) * command.x
        current_y += (command.steps / STEPS_PER_MM) * command.y
        set_position(current_x, current_y)


# Remaps coords to have 0,0 in the top left
def set_position(x: int, y: int):
    # t.setpos(x - WIDTH, HEIGHT - y)
    x_offset = t.screen.window_width() // 2
    y_offset = t.screen.window_height() // 2
    t.setpos(x - x_offset, y_offset - y)


if __name__ == "__main__":
    main()
