import time
import board
import digitalio

cs = digitalio.DigitalInOut(board.GP17)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True

print("CS output HIGH")

while True:
    print("Pico running")
    time.sleep(1)