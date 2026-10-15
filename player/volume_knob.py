"""Volume knob: 10k potentiometer read by an MCP3008 ADC over SPI0.

The Raspberry Pi has no analog inputs, so the MCP3008 converts the
potentiometer voltage (0 - 3.3 V) into a 10-bit number. The Adafruit
library scales it to 0 - 65535; we turn that into 0 - 100 %.
"""

import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

CHANNELS = [MCP.P0, MCP.P1, MCP.P2, MCP.P3, MCP.P4, MCP.P5, MCP.P6, MCP.P7]


class VolumeKnob:
    def __init__(self, spi_names, cs_name, channel=0, deadband=3):
        clock, mosi, miso = (getattr(board, name) for name in spi_names)
        self.spi = busio.SPI(clock=clock, MOSI=mosi, MISO=miso)
        self.cs = digitalio.DigitalInOut(getattr(board, cs_name))
        self.mcp = MCP.MCP3008(self.spi, self.cs)
        self.channel = AnalogIn(self.mcp, CHANNELS[channel])

        self.deadband = deadband
        self.percent = self._read_percent()

    def _read_percent(self):
        return round(self.channel.value / 65535 * 100)

    def read(self):
        """Return (volume %, changed). Small changes are ignored (noise)."""
        new = self._read_percent()
        if abs(new - self.percent) >= self.deadband or (new in (0, 100) and new != self.percent):
            self.percent = new
            return self.percent, True
        return self.percent, False

    def close(self):
        self.cs.deinit()
        self.spi.deinit()
