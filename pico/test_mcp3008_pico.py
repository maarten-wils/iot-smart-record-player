import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


# SPI0
spi = busio.SPI(
    clock=board.GP18,
    MOSI=board.GP19,
    MISO=board.GP16
)

# MCP3008 chip select
cs = digitalio.DigitalInOut(board.GP17)

# MCP3008
mcp = MCP.MCP3008(spi, cs)

# Potentiometer on channel 0
channel = AnalogIn(mcp, MCP.P0)

print("MCP3008 potentiometer test")
print("Turn the knob. Ctrl+C to stop.")

while True:
    raw = channel.value
    voltage = channel.voltage
    percent = round(raw / 65535 * 100)

    print(
        "raw {:5d} | {:.2f} V | {:3d} %".format(
            raw,
            voltage,
            percent
        )
    )

    time.sleep(0.3)