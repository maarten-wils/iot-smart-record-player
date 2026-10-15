"""28BYJ-48 stepper motor (platter) via ULN2003.

The motor runs in its own thread (course chapter 5: multithreading), so
reading sensors, updating the OLED or waiting for the network never makes
the platter stutter.
"""

import threading
import time

import board
import digitalio

# Wave drive: one coil at a time (course approach).
STEPS = [
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True),
]


class Stepper:
    def __init__(self, pin_names, delay=0.01, reverse=False):
        self.delay = delay
        self.direction = -1 if reverse else 1

        self.outputs = []
        for name in pin_names:
            output = digitalio.DigitalInOut(getattr(board, name))
            output.direction = digitalio.Direction.OUTPUT
            self.outputs.append(output)

        self._running = threading.Event()   # set = platter turns
        self._closing = threading.Event()   # set = thread must end
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def start(self):
        self._running.set()

    def stop(self):
        self._running.clear()

    @property
    def running(self):
        return self._running.is_set()

    def _coils_off(self):
        for output in self.outputs:
            output.value = False

    def _run(self):
        step_number = 0
        coils_on = False

        while not self._closing.is_set():
            if self._running.is_set():
                for output, value in zip(self.outputs, STEPS[step_number % 4]):
                    output.value = value
                coils_on = True
                step_number += self.direction
                time.sleep(self.delay)
            else:
                if coils_on:
                    # Switch the coils off when stopped: no heat, no current.
                    self._coils_off()
                    coils_on = False
                self._running.wait(timeout=0.1)

    def close(self):
        self._closing.set()
        self._running.set()          # wake the thread so it can end
        self._thread.join(timeout=1)
        self._coils_off()
        for output in self.outputs:
            output.deinit()
