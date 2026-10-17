import time
import board
import pwmio

# Hardware PWM LED on Pico GP12.
led_pwm = pwmio.PWMOut(
    board.GP12,
    frequency=5000,
    duty_cycle=0
)

try:
    while True:
        led_pwm.duty_cycle = 10000
        time.sleep(1)

        led_pwm.duty_cycle = 50000
        time.sleep(1)

finally:
    led_pwm.duty_cycle = 0
    led_pwm.deinit()