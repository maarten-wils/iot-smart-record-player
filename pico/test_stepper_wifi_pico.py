import os
import time
import board
import digitalio
import wifi

# Diagnostic test: same verified stepper test, but with WiFi active.
# This isolates whether the motor problem appears when the Pico is under
# the extra load of the normal runtime.

print("Connecting to WiFi", os.getenv("CIRCUITPY_WIFI_SSID"))
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"),
    os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
print("WiFi connected:", wifi.radio.ipv4_address)

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
    print("WiFi stepper test starting")

    for i in range(2048):
        step = steps[i % 4]

        for output, value in zip(outputs, step):
            output.value = value

        time.sleep(0.01)

finally:
    for output in outputs:
        output.value = False
        output.deinit()

    print("WiFi stepper test finished")
