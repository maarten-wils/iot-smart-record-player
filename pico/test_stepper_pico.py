import time
import board
import digitalio

# Pico GPIO pins connected to ULN2003 IN1-IN4.
pins = [
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9
]

outputs = []

for pin in pins:
    output = digitalio.DigitalInOut(pin)
    output.direction = digitalio.Direction.OUTPUT
    outputs.append(output)

steps = [
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True)
]

try:
    print("Pico stepper test starting")

    for i in range(2048):
        step = steps[i % 4]

        for output, value in zip(outputs, step):
            output.value = value

        time.sleep(0.01)

finally:
    for output in outputs:
        output.value = False
        output.deinit()

    print("Pico stepper test finished")