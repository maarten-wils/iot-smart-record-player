import board
import busio
import displayio
from fourwire import FourWire
import adafruit_displayio_ssd1306

displayio.release_displays()

# OLED on SPI1: SCL = clock, SDA = MOSI.
spi = busio.SPI(
    board.GP10,
    MOSI=board.GP11
)

# OLED control pins.
oled_dc = board.GP13
oled_reset = board.GP22

# OLED has no physical CS pin.
# GP5 is only used because FourWire requires a CS pin.
oled_cs = board.GP5

display_bus = FourWire(
    spi,
    command=oled_dc,
    chip_select=oled_cs,
    reset=oled_reset,
    baudrate=1000000
)

display = adafruit_displayio_ssd1306.SSD1306(
    display_bus,
    width=128,
    height=64
)

# Make the whole OLED white.
group = displayio.Group()
display.root_group = group

bitmap = displayio.Bitmap(128, 64, 1)
palette = displayio.Palette(1)
palette[0] = 0xFFFFFF

tile = displayio.TileGrid(
    bitmap,
    pixel_shader=palette
)

group.append(tile)

print("DisplayIO OLED SPI1 test running")

while True:
    pass