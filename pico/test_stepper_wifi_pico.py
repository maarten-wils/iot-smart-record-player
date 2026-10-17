import os
import time
import board
import digitalio
import wifi


# ---------- WiFi ----------

WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")

print("Connecting to WiFi")

wifi.radio.connect(
    WIFI_SSID,
    WIFI_PASSWORD
)

print("WiFi connected")


# ---------- Stepper ----------

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
    print("Stepper + WiFi test starting")

    # Exact same motor loop as the working standalone test.
    for i in range(2048):
        step = steps[i % 4]

        for output, value in zip(outputs, step):
            output.value = value

        time.sleep(0.01)

finally:
    for output in outputs:
        output.value = False
        output.deinit()

    print("Stepper + WiFi test finished")