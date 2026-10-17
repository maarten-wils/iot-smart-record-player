import time
import board
import busio
import digitalio
import pwmio
import displayio
from fourwire import FourWire

import adafruit_hcsr04
import adafruit_displayio_ssd1306
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import mfrc522


# -------------------------
# BH1750 light sensor
# -------------------------

BH1750_ADDRESS = 0x23

i2c = busio.I2C(
    board.GP1,   # SCL
    board.GP0    # SDA
)

while not i2c.try_lock():
    pass

i2c.writeto(BH1750_ADDRESS, bytes([0x10]))
i2c.unlock()

time.sleep(0.2)


def read_lux():
    data = bytearray(2)

    while not i2c.try_lock():
        pass

    i2c.readfrom_into(BH1750_ADDRESS, data)
    i2c.unlock()

    value = (data[0] << 8) | data[1]
    return value / 1.2


# -------------------------
# HC-SR04
# -------------------------

sonar = adafruit_hcsr04.HCSR04(
    trigger_pin=board.GP2,
    echo_pin=board.GP3
)


# -------------------------
# Pushbutton
# -------------------------

button = digitalio.DigitalInOut(board.GP15)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

previous_button = button.value


# -------------------------
# PWM LED
# -------------------------

pwm_led = pwmio.PWMOut(
    board.GP12,
    frequency=5000,
    duty_cycle=10000
)


# -------------------------
# Stepper motor
# -------------------------

stepper_pins = [
    digitalio.DigitalInOut(board.GP6),
    digitalio.DigitalInOut(board.GP7),
    digitalio.DigitalInOut(board.GP8),
    digitalio.DigitalInOut(board.GP9)
]

for pin in stepper_pins:
    pin.direction = digitalio.Direction.OUTPUT


step_sequence = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
]


def move_stepper(steps):
    for step in range(steps):
        pattern = step_sequence[step % 4]

        for pin, value in zip(stepper_pins, pattern):
            pin.value = value

        time.sleep(0.01)

    for pin in stepper_pins:
        pin.value = False


# -------------------------
# OLED on SPI1
# -------------------------

displayio.release_displays()

oled_spi = busio.SPI(
    board.GP10,
    MOSI=board.GP11
)

oled_bus = FourWire(
    oled_spi,
    command=board.GP13,
    chip_select=board.GP5,
    reset=board.GP22,
    baudrate=1000000
)

display = adafruit_displayio_ssd1306.SSD1306(
    oled_bus,
    width=128,
    height=64
)

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


# -------------------------
# Shared SPI0
# MCP3008 + RC522
# -------------------------

spi = busio.SPI(
    board.GP18,       # SCK
    MOSI=board.GP19,
    MISO=board.GP16
)


# MCP3008
mcp_cs = digitalio.DigitalInOut(board.GP17)

mcp = MCP.MCP3008(
    spi,
    mcp_cs
)

volume = AnalogIn(
    mcp,
    MCP.P0
)


# RC522
rfid_cs = digitalio.DigitalInOut(board.GP20)
rfid_rst = digitalio.DigitalInOut(board.GP21)

rfid = mfrc522.MFRC522(
    spi,
    rfid_cs,
    rfid_rst
)


# -------------------------
# Combined test
# -------------------------

print("Starting full Pico hardware test")

move_stepper(2048)

print("Stepper test finished")


while True:
    lux = read_lux()

    raw = volume.value
    percent = round(raw / 65535 * 100)

    try:
        distance = sonar.distance

        print(
            "Distance: {:.1f} cm | Light: {:.2f} lux | Volume: {:3d}%".format(
                distance,
                lux,
                percent
            )
        )

    except RuntimeError:
        print(
            "Distance: no reading | Light: {:.2f} lux | Volume: {:3d}%".format(
                lux,
                percent
            )
        )

    # Button
    if button.value != previous_button:
        if button.value:
            print("RELEASED")
        else:
            print("PRESSED")

        previous_button = button.value

    # RFID
    status, tag_type = rfid.request(rfid.REQALL)

    if status == rfid.OK:
        status, uid = rfid.anticoll()

        if status == rfid.OK:
            uid_text = "{:02x}{:02x}{:02x}{:02x}".format(
                uid[0],
                uid[1],
                uid[2],
                uid[3]
            )

            print("Tag detected! UID:", uid_text)

    # PWM LED
    if pwm_led.duty_cycle == 10000:
        pwm_led.duty_cycle = 50000
    else:
        pwm_led.duty_cycle = 10000

    time.sleep(1)