import RPi.GPIO as GPIO
import time
import json

from sys import argv
from enum import Enum
from command import Command

# 21 mm horizontally
# 19 mm vertically

SCREEN_HEIGHT_MM = 133
SCREEN_WIDTH_MM = 185

X_MOTOR_PINS = [17, 18, 27, 22]
Y_MOTOR_PINS = [5, 6, 12, 13]

STEP_SLEEP_SECS = 0.002  # careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
STEPS_PER_TURN = 4096  # 5.625*(1/64) per step, 4096 steps is 360°
BACKLASH_COMPENSATION_STEPS = 200  # Number of steps needed to compensate for backlash

# stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
STEP_SEQUENCE = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
]


class Direction(Enum):
    POSITIVE = 1
    ZERO = 0
    NEGATIVE = -1


x_motor_sequence_index = 0
y_motor_sequence_index = 0

current_x_dir = Direction.ZERO
current_y_dir = Direction.ZERO


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


def draw_from_file(commands: list[Command]):
    for command in commands:
        print(repr(command))
        spin_motor(command.steps, Direction(command.x), Direction(command.y))


def setup_gpio():
    # set up pins
    GPIO.setmode(GPIO.BCM)

    for pin in X_MOTOR_PINS:
        GPIO.setup(pin, GPIO.OUT)

    for pin in Y_MOTOR_PINS:
        GPIO.setup(pin, GPIO.OUT)

    # initialize to low
    for pin in X_MOTOR_PINS:
        GPIO.output(pin, GPIO.LOW)

    for pin in Y_MOTOR_PINS:
        GPIO.output(pin, GPIO.LOW)


def cleanup_gpio():
    for pin in X_MOTOR_PINS:
        GPIO.output(pin, GPIO.LOW)

    for pin in Y_MOTOR_PINS:
        GPIO.output(pin, GPIO.LOW)

    GPIO.cleanup()


def main():
    if len(argv) != 2:
        print("Nuh uh! Supply a single argument please")
        return

    commands = load_file(argv[1])

    print("Moving pen to top left...")
    reset_pen()

    input("Shake the Etch-a-Sketch to clear it, then press enter to continue: ")
    print(f"Drawing {argv[1]}...")

    draw_from_file(commands)


# Move the pen to the top left
def reset_pen():
    spin_motor(5 * STEPS_PER_TURN, x_dir=Direction.NEGATIVE, y_dir=Direction.NEGATIVE)


def spin_motor(step_count: int, x_dir: Direction, y_dir: Direction):
    global x_motor_sequence_index, y_motor_sequence_index
    global current_x_dir, current_y_dir

    x_fuel = step_count
    y_fuel = step_count

    if (
        current_x_dir != Direction.ZERO
        and x_dir != Direction.ZERO
        and current_x_dir != x_dir
    ):
        x_fuel += BACKLASH_COMPENSATION_STEPS

    if (
        current_y_dir != Direction.ZERO
        and y_dir != Direction.ZERO
        and current_y_dir != y_dir
    ):
        y_fuel += BACKLASH_COMPENSATION_STEPS

    if x_dir != Direction.ZERO:
        current_x_dir = x_dir
    if y_dir != Direction.ZERO:
        current_y_dir = y_dir

    while x_fuel > 0 or y_fuel > 0:
        if x_fuel >= y_fuel:
            x_fuel -= 1

            if x_dir != Direction.ZERO:
                for pin in range(0, 4):
                    GPIO.output(
                        X_MOTOR_PINS[pin], STEP_SEQUENCE[x_motor_sequence_index][pin]
                    )

                match x_dir:
                    case Direction.NEGATIVE:
                        x_motor_sequence_index = (x_motor_sequence_index + 1) % 8
                    case Direction.POSITIVE:
                        x_motor_sequence_index = (x_motor_sequence_index - 1) % 8

        if y_fuel >= x_fuel:
            y_fuel -= 1

            if y_dir != Direction.ZERO:
                for pin in range(0, 4):
                    GPIO.output(
                        Y_MOTOR_PINS[pin], STEP_SEQUENCE[y_motor_sequence_index][pin]
                    )

                match y_dir:
                    case Direction.NEGATIVE:
                        y_motor_sequence_index = (y_motor_sequence_index - 1) % 8
                    case Direction.POSITIVE:
                        y_motor_sequence_index = (y_motor_sequence_index + 1) % 8

        time.sleep(STEP_SLEEP_SECS)


if __name__ == "__main__":
    try:
        setup_gpio()
        main()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_gpio()
        exit(0)
