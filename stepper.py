import gpiod
import time

HALF_STEP_SEQ = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

class StepperMotor:
    def __init__(self, chip_name, control_pins):
        self.chip = gpiod.Chip(chip_name)
        self.lines = [self.chip.get_line(pin) for pin in control_pins]
        for line in self.lines:
            line.request(consumer='stepper_motor', type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])

    def step(self, steps, direction='right', delay=0.001):
        seq = HALF_STEP_SEQ if direction == 'right' else list(reversed(HALF_STEP_SEQ))
        for _ in range(steps):
            for halfstep in seq:
                for pin, val in zip(self.lines, halfstep):
                    pin.set_value(val)
                time.sleep(delay)

    def release(self):
        for line in self.lines:
            line.set_value(0)
            line.release()

class Robot:
    def __init__(self):
        self.left_motor = StepperMotor('gpiochip4', [14, 15, 18, 23])
        self.right_motor = StepperMotor('gpiochip4', [24, 25, 8, 7])
        self.delay = 0.001
        self.step_count = 512

    def forward(self):
        for _ in range(self.step_count):
            self.left_motor.step(1, 'right', self.delay)
            self.right_motor.step(1, 'right', self.delay)

    def backward(self):
        for _ in range(self.step_count):
            self.left_motor.step(1, 'left', self.delay)
            self.right_motor.step(1, 'left', self.delay)

    def left(self):
        for _ in range(self.step_count):
            self.left_motor.step(1, 'left', self.delay)
            self.right_motor.step(1, 'right', self.delay)

    def right(self):
        for _ in range(self.step_count):
            self.left_motor.step(1, 'right', self.delay)
            self.right_motor.step(1, 'left', self.delay)

    def stop(self):
        self.left_motor.release()
        self.right_motor.release()

if __name__ == "__main__":
    robot = Robot()
    try:
        robot.forward()
        time.sleep(1)
        robot.left()
        time.sleep(1)
        robot.backward()
    finally:
        robot.stop()
