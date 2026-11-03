import time
import board
import busio
import displayio
import terminalio

from fourwire import FourWire
import adafruit_displayio_ssd1306
from adafruit_display_text import label

# Standalone OLED text test using the same SPI1 wiring as pico/code.py.
displayio.release_displays()

spi = busio.SPI(
    board.GP10,
    MOSI=board.GP11
)

bus = FourWire(
    spi,
    command=board.GP13,
    chip_select=board.GP5,
    reset=board.GP22,
    baudrate=1000000
)

display = adafruit_displayio_ssd1306.SSD1306(
    bus,
    width=128,
    height=64
)

group = displayio.Group()
display.root_group = group

status = label.Label(
    terminalio.FONT,
    text="REST",
    color=0xFFFFFF,
    scale=2,
    x=5,
    y=14
)

detail = label.Label(
    terminalio.FONT,
    text="OLED text test",
    color=0xFFFFFF,
    scale=1,
    x=5,
    y=38
)

group.append(status)
group.append(detail)

states = [
    ("REST", "Ready"),
    ("PLAY", "Artist - Title"),
    ("PAUSE", "Playback paused"),
    ("OFF", "Standby"),
]

while True:
    for state, text in states:
        status.text = state
        detail.text = text
        print(state, "-", text)
        time.sleep(2)
