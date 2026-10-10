import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# SPI1 for OLED without an external CS pin.
spi = busio.SPI(board.D21, board.D20, board.D19)

# Control pins from the course example.
oled_reset = digitalio.DigitalInOut(board.D4)
oled_dc = digitalio.DigitalInOut(board.D6)

# The OLED has no physical CS pin.
# GPIO18 is used as the SPI1 CS object required by the library.
oled_cs = digitalio.DigitalInOut(board.D18)

WIDTH = 128
HEIGHT = 64

# Initialize the SSD1306 OLED.
oled = adafruit_ssd1306.SSD1306_SPI(
    WIDTH,
    HEIGHT,
    spi,
    oled_dc,
    oled_reset,
    oled_cs
)

# Clear the display.
oled.fill(0)
oled.show()

# Create a 1-bit image and draw text.
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

draw.text((10, 10), "IoT Smart", font=font, fill=255)
draw.text((10, 25), "Record Player", font=font, fill=255)
draw.text((10, 40), "OLED TEST", font=font, fill=255)

# Show the image.
oled.image(image)
oled.show()

print("OLED test finished")
