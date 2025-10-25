import RPi.GPIO as GPIO
import time
from enum import Enum

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

motor_step_counter = 0


# 21 mm horizontally
# 19 mm vertically

# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.001

step_count = 4096  # 5.625*(1/64) per step, 4096 steps is 360°

direction = False  # True for clockwise, False for counter-clockwise

# defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
step_sequence = [
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


def setup():
    # setting up
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(x_in1, GPIO.OUT)
    GPIO.setup(x_in2, GPIO.OUT)
    GPIO.setup(x_in3, GPIO.OUT)
    GPIO.setup(x_in4, GPIO.OUT)

    GPIO.setup(y_in1, GPIO.OUT)
    GPIO.setup(y_in2, GPIO.OUT)
    GPIO.setup(y_in3, GPIO.OUT)
    GPIO.setup(y_in4, GPIO.OUT)

    # initializing
    GPIO.output(x_in1, GPIO.LOW)
    GPIO.output(x_in2, GPIO.LOW)
    GPIO.output(x_in3, GPIO.LOW)
    GPIO.output(x_in4, GPIO.LOW)

    GPIO.output(y_in1, GPIO.LOW)
    GPIO.output(y_in2, GPIO.LOW)
    GPIO.output(y_in3, GPIO.LOW)
    GPIO.output(y_in4, GPIO.LOW)


def cleanup():
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
    spin_motor(step_count, x_dir=Direction.NEGATIVE, y_dir=Direction.ZERO)
    # spin_motor(step_count, x_dir=Direction.ZERO, y_dir=Direction.POSITIVE)


def spin_motor(step_count: int, x_dir: Direction, y_dir: Direction):
    global motor_step_counter

    if x_dir != Direction.ZERO:
        direction = x_dir
        motor_pins = x_motor_pins
    elif y_dir != Direction.ZERO:
        direction = y_dir
        motor_pins = y_motor_pins

    i = 0
    for i in range(step_count):
        for pin in range(0, len(motor_pins)):
            # assert motor_step_counter >= 0 and motor_step_counter < 8
            GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
        match direction:
            case Direction.NEGATIVE:
                motor_step_counter = (motor_step_counter - 1) % 8
            case Direction.POSITIVE:
                motor_step_counter = (motor_step_counter + 1) % 8
            case Direction.ZERO:
                pass

        time.sleep(step_sleep)


if __name__ == "__main__":
    try:
        setup()
        main()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
        exit(0)
