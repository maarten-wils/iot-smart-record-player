"""PWM status LED.

STANDBY -> off, REST -> dim, PLAY -> bright, PAUSED -> slow "breathing".
"""

import math
import time

import board
import pwmio

from . import state


class StatusLed:
    def __init__(self, pin_name, frequency, dim, bright):
        self.dim = dim
        self.bright = bright
        self.pwm = pwmio.PWMOut(getattr(board, pin_name), frequency=frequency, duty_cycle=0)

    def update(self, status):
        """Call regularly from the main loop; breathing needs repeated updates."""
        if status == state.PLAY:
            duty = self.bright
        elif status == state.PAUSED:
            # Sine wave between 0 and bright, period 2 seconds.
            level = (math.sin(time.monotonic() * math.pi) + 1) / 2
            duty = int(level * self.bright)
        elif status == state.REST:
            duty = self.dim
        else:
            duty = 0
        self.pwm.duty_cycle = duty

    def close(self):
        self.pwm.duty_cycle = 0
        self.pwm.deinit()
