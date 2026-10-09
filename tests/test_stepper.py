import time
import board
import digitalio

# GPIO pins connected to ULN2003 IN1-IN4.
pins = [
    board.D17,
    board.D18,
    board.D27,
    board.D22
]

outputs = []

# Configure the four GPIO pins as outputs.
for pin in pins:
    output = digitalio.DigitalInOut(pin)
    output.direction = digitalio.Direction.OUTPUT
    outputs.append(output)

# Wave drive: activate one coil at a time.
steps = [
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True)
]

try:
    print("Stepper test starting")

    for i in range(512):
        step = steps[i % 4]

        for output, value in zip(outputs, step):
            output.value = value

        time.sleep(0.01)

finally:
    # Switch off all motor coils.
    for output in outputs:
        output.value = False
        output.deinit()

    print("Stepper test finished")
