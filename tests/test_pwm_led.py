import board
import pwmio
import time

# Hardware PWM LED on GPIO12.
led_pwm = pwmio.PWMOut(
    board.D12,
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