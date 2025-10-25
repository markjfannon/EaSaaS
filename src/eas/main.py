import RPi.GPIO as GPIO
import time
from enum import Enum

# 21 mm horizontally
# 19 mm vertically

SCREEN_HEIGHT_MM = 133
SCREEN_WIDTH_MM = 185

x_in1 = 17
x_in2 = 18
x_in3 = 27
x_in4 = 22

y_in1 = 5
y_in2 = 6
y_in3 = 12
y_in4 = 13

x_motor_pins = [x_in1, x_in2, x_in3, x_in4]
y_motor_pins = [y_in1, y_in2, y_in3, y_in4]

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
    GPIO.setup(x_in1, GPIO.OUT)
    GPIO.setup(x_in2, GPIO.OUT)
    GPIO.setup(x_in3, GPIO.OUT)
    GPIO.setup(x_in4, GPIO.OUT)

    GPIO.setup(y_in1, GPIO.OUT)
    GPIO.setup(y_in2, GPIO.OUT)
    GPIO.setup(y_in3, GPIO.OUT)
    GPIO.setup(y_in4, GPIO.OUT)

    # initialize to low
    GPIO.output(x_in1, GPIO.LOW)
    GPIO.output(x_in2, GPIO.LOW)
    GPIO.output(x_in3, GPIO.LOW)
    GPIO.output(x_in4, GPIO.LOW)

    GPIO.output(y_in1, GPIO.LOW)
    GPIO.output(y_in2, GPIO.LOW)
    GPIO.output(y_in3, GPIO.LOW)
    GPIO.output(y_in4, GPIO.LOW)


def cleanup_gpio():
    GPIO.output(x_in1, GPIO.LOW)
    GPIO.output(x_in2, GPIO.LOW)
    GPIO.output(x_in3, GPIO.LOW)
    GPIO.output(x_in4, GPIO.LOW)

    GPIO.output(y_in1, GPIO.LOW)
    GPIO.output(y_in2, GPIO.LOW)
    GPIO.output(y_in3, GPIO.LOW)
    GPIO.output(y_in4, GPIO.LOW)

    GPIO.cleanup()


def main():
    spin_motor(STEPS_PER_TURN, x_dir=Direction.ZERO, y_dir=Direction.POSITIVE)


def spin_motor(step_count: int, x_dir: Direction, y_dir: Direction):
    global x_motor_sequence_index, y_motor_sequence_index

    for _ in range(step_count):
        for pin in range(0, 4):
            GPIO.output(x_motor_pins[pin], STEP_SEQUENCE[x_motor_sequence_index][pin])
            GPIO.output(y_motor_pins[pin], STEP_SEQUENCE[y_motor_sequence_index][pin])

        match x_dir:
            case Direction.NEGATIVE:
                x_motor_sequence_index = (x_motor_sequence_index - 1) % 8
            case Direction.POSITIVE:
                x_motor_sequence_index = (x_motor_sequence_index + 1) % 8
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
