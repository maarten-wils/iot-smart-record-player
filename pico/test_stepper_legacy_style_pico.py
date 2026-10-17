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


# Same wave-drive sequence as last weekend.
steps = [
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True)
]


step_number = 0

print("Legacy-style Pico stepper test starting")

try:
    while True:
        step = steps[step_number % 4]

        for output, value in zip(outputs, step):
            output.value = value

        # Same direction as last weekend's Pi test.
        step_number -= 1

        # Same fixed loop delay as last weekend.
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    for output in outputs:
        output.value = False
        output.deinit()

    print("Stepper test finished")