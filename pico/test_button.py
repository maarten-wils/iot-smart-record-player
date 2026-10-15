# Pico test 2: pushbutton alone, no WiFi or MQTT.
# Button between GP15 (pin 20) and GND (pin 18), internal pull-up.
# Copy this file to the Pico as code.py, watch the console in Thonny.
# Expected: PRESSED / RELEASED, onboard LED on while pressed.

import time
import board
import digitalio

button = digitalio.DigitalInOut(board.GP15)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

last = None
while True:
    pressed = not button.value          # pull-up: pressed reads False
    led.value = pressed
    if pressed != last:
        print("PRESSED" if pressed else "RELEASED")
        last = pressed
    time.sleep(0.02)
