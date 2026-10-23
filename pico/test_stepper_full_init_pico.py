import os
import time
import board
import busio
import digitalio
import pwmio
import displayio
import wifi

from fourwire import FourWire
import adafruit_hcsr04
import adafruit_displayio_ssd1306
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import mfrc522

# Diagnostic: initialize the same hardware as the full runtime,
# then run the exact verified standalone stepper loop.

print("Init HC-SR04")
sonar = adafruit_hcsr04.HCSR04(
    trigger_pin=board.GP2,
    echo_pin=board.GP3,
    timeout=0.05
)

print("Init button")
button = digitalio.DigitalInOut(board.GP15)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

print("Init LEDs")
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
status_led = pwmio.PWMOut(board.GP12, frequency=5000, duty_cycle=10000)

print("Init OLED")
displayio.release_displays()
oled_spi = busio.SPI(board.GP10, MOSI=board.GP11)
oled_bus = FourWire(
    oled_spi,
    command=board.GP13,
    chip_select=board.GP5,
    reset=board.GP22,
    baudrate=1000000
)
display = adafruit_displayio_ssd1306.SSD1306(oled_bus, width=128, height=64)

print("Init BH1750")
i2c = busio.I2C(board.GP1, board.GP0)
while not i2c.try_lock():
    pass
i2c.writeto(0x23, bytes([0x10]))
i2c.unlock()

print("Init MCP3008 + RC522")
spi = busio.SPI(board.GP18, MOSI=board.GP19, MISO=board.GP16)
mcp_cs = digitalio.DigitalInOut(board.GP17)
mcp = MCP.MCP3008(spi, mcp_cs)
volume_channel = AnalogIn(mcp, MCP.P0)
rfid_cs = digitalio.DigitalInOut(board.GP20)
rfid_rst = digitalio.DigitalInOut(board.GP21)
rfid = mfrc522.MFRC522(spi, rfid_cs, rfid_rst)

print("Connecting WiFi")
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"),
    os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
print("WiFi connected:", wifi.radio.ipv4_address)

print("Init stepper")
pins = [board.GP6, board.GP7, board.GP8, board.GP9]
outputs = []
for pin in pins:
    output = digitalio.DigitalInOut(pin)
    output.direction = digitalio.Direction.OUTPUT
    outputs.append(output)

steps = [
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True)
]

try:
    print("Full-init stepper test starting")
    for i in range(2048):
        step = steps[i % 4]
        for output, value in zip(outputs, step):
            output.value = value
        time.sleep(0.01)
finally:
    for output in outputs:
        output.value = False
        output.deinit()
    print("Full-init stepper test finished")
