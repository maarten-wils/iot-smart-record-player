import time
import board
import digitalio

# Diagnostic: find the smallest uninterrupted block that visibly moves
# the stepper while keeping the same verified 10 ms step delay.

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

step_index = 0

try:
    for block_size in (4, 16, 32, 64):
        print("Testing block:", block_size, "steps")

        for _ in range(block_size):
            step = steps[step_index]
            for output, value in zip(outputs, step):
                output.value = value

            step_index = (step_index + 1) % len(steps)
            time.sleep(0.01)

        for output in outputs:
            output.value = False

        print("Pause")
        time.sleep(2)

finally:
    for output in outputs:
        output.value = False
        output.deinit()

    print("Chunk test finished")
