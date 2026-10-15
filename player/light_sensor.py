"""BH1750 light sensor via I2C: detects the tonearm position.

Tonearm on its rest -> covers the sensor -> low lux -> REST.
Tonearm on the record -> sensor free -> more lux -> PLAY.
"""

import board
import busio

COMMAND_HIGH_RES = bytearray([0x10])  # 1 lx resolution, see datasheet


class LightSensor:
    def __init__(self, scl_name, sda_name, address=0x23):
        self.address = address
        self.i2c = busio.I2C(getattr(board, scl_name), getattr(board, sda_name))

    def read_lux(self):
        """Return the light level in lux, or None if the bus was busy."""
        if not self.i2c.try_lock():
            return None
        try:
            result = bytearray(2)
            self.i2c.writeto_then_readfrom(self.address, COMMAND_HIGH_RES, result)
            return ((result[0] << 8) | result[1]) / 1.2   # conversion from datasheet
        finally:
            self.i2c.unlock()

    def close(self):
        self.i2c.deinit()
