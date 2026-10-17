import board
import busio
import digitalio
import adafruit_ssd1306

spi = busio.SPI(
    board.GP18,
    MOSI=board.GP19
)

oled_dc = digitalio.DigitalInOut(board.GP6)
oled_reset = digitalio.DigitalInOut(board.GP7)
oled_cs = digitalio.DigitalInOut(board.GP17)

oled = adafruit_ssd1306.SSD1306_SPI(
    128,
    64,
    spi,
    oled_dc,
    oled_reset,
    oled_cs,
    baudrate=500000
)

oled.fill(1)
oled.show()

print("OLED SPI0 full-screen test finished")