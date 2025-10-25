import RPi.GPIO as GPIO
import time
from enum import Enum

# 21 mm horizontally
# 19 mm vertically

SCREEN_HEIGHT_MM = 133
SCREEN_WIDTH_MM = 185

X_MOTOR_PINS = [17, 18, 27, 22]
Y_MOTOR_PINS = [5, 6, 12, 13]

STEP_SLEEP_SECS = 0.002  # careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
STEPS_PER_TURN = 4096  # 5.625*(1/64) per step, 4096 steps is 360°

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

x_motor_sequence_index = 0
y_motor_sequence_index = 0


class Direction(Enum):
    POSITIVE = 1
    ZERO = 0
    NEGATIVE = -1


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
    spin_motor(STEPS_PER_TURN, x_dir=Direction.POSITIVE, y_dir=Direction.ZERO)
    spin_motor(STEPS_PER_TURN, x_dir=Direction.ZERO, y_dir=Direction.POSITIVE)
    spin_motor(STEPS_PER_TURN, x_dir=Direction.NEGATIVE, y_dir=Direction.ZERO)
    spin_motor(STEPS_PER_TURN, x_dir=Direction.ZERO, y_dir=Direction.NEGATIVE)


def spin_motor(step_count: int, x_dir: Direction, y_dir: Direction):
    global x_motor_sequence_index, y_motor_sequence_index

    for _ in range(step_count):
        if x_dir != Direction.ZERO:
            for pin in range(0, 4):
                GPIO.output(
                    X_MOTOR_PINS[pin], STEP_SEQUENCE[x_motor_sequence_index][pin]
                )

        if y_dir != Direction.ZERO:
            for pin in range(0, 4):
                GPIO.output(
                    Y_MOTOR_PINS[pin], STEP_SEQUENCE[y_motor_sequence_index][pin]
                )

        match x_dir:
            case Direction.NEGATIVE:
                x_motor_sequence_index = (x_motor_sequence_index + 1) % 8
            case Direction.POSITIVE:
                x_motor_sequence_index = (x_motor_sequence_index - 1) % 8
            case Direction.ZERO:
                pass

        match y_dir:
            case Direction.NEGATIVE:
                y_motor_sequence_index = (y_motor_sequence_index - 1) % 8
            case Direction.POSITIVE:
                y_motor_sequence_index = (y_motor_sequence_index + 1) % 8
            case Direction.ZERO:
                pass

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
