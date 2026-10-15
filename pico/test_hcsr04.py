# Pico test 1: HC-SR04 alone, no WiFi or MQTT.
# Copy this file to the Pico as code.py, watch the console in Thonny.
# Expected: a distance in cm twice per second; move your hand to see it change.

import time
import board
import adafruit_hcsr04

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP2, echo_pin=board.GP3)

while True:
    try:
        print("Distance: %.1f cm" % sonar.distance)
    except RuntimeError:
        print("No echo (nothing in range or wiring problem)")
    time.sleep(0.5)
