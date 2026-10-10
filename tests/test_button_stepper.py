import time
import board
import digitalio

# Stepper GPIO pins.
pins = [
    board.D17,
    board.D18,
    board.D27,
    board.D22
]

outputs = []

for pin in pins:
    output = digitalio.DigitalInOut(pin)
    output.direction = digitalio.Direction.OUTPUT
    outputs.append(output)

# Stepper sequence.
steps = [
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True)
]

# Pushbutton on GPIO23.
button = digitalio.DigitalInOut(board.D23)
button.direction = digitalio.Direction.INPUT

step_number = 0

try:
    while True:
        if button.value:
            # Button released: stop motor.
            for output in outputs:
                output.value = False

            time.sleep(0.01)

        else:
            # Button pressed: rotate motor.
            step = steps[step_number % 4]

            for output, value in zip(outputs, step):
                output.value = value

            step_number += 1
            time.sleep(0.01)

finally:
    for output in outputs:
        output.value = False
        output.deinit()

    button.deinit()
