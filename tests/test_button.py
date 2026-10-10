import board
import digitalio
import time

# Configure GPIO23 as a digital input.
button = digitalio.DigitalInOut(board.D23)
button.direction = digitalio.Direction.INPUT

try:
    while True:
        if button.value:
            print("RELEASED")
        else:
            print("PRESSED")

        time.sleep(0.5)

finally:
    button.deinit()
