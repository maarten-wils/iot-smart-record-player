import time
import subprocess
import board
import busio
import digitalio
import pwmio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Stepper GPIO pins.
pins = [
    board.D17,
    board.D26,
    board.D27,
    board.D22
]

outputs = []

for pin in pins:
    output = digitalio.DigitalInOut(pin)
    output.direction = digitalio.Direction.OUTPUT
    outputs.append(output)

# Wave drive step sequence.
steps = [
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True)
]

# Start I2C communication with the BH1750.
i2c = busio.I2C(board.D3, board.D2)

# PWM status LED on GPIO12.
led_pwm = pwmio.PWMOut(
    board.D12,
    frequency=5000,
    duty_cycle=10000
)

# SPI1 OLED without a physical CS pin.
spi = busio.SPI(board.D21, board.D20, board.D19)
oled_reset = digitalio.DigitalInOut(board.D4)
oled_dc = digitalio.DigitalInOut(board.D6)
oled_cs = digitalio.DigitalInOut(board.D5)

oled = adafruit_ssd1306.SSD1306_SPI(
    128,
    64,
    spi,
    oled_dc,
    oled_reset,
    oled_cs
)

font = ImageFont.load_default()

ADDRESS = 0x23
COMMAND_HIGH_RES = bytearray([0x10])
LIGHT_THRESHOLD = 4
AUDIO_FILE = "audio/avalon-1920.ogg"


def get_light_level(i2c_bus, addr):
    result = bytearray(2)

    i2c_bus.writeto_then_readfrom(
        addr,
        COMMAND_HIGH_RES,
        result
    )

    return ((result[0] << 8) | result[1]) / 1.2


def show_status(status):
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    draw.text((10, 10), "Record Player", font=font, fill=255)

    if status == "PLAY":
        draw.text((10, 30), "PLAY", font=font, fill=255)

        # Simple music note.
        draw.ellipse((90, 38, 98, 46), outline=255, fill=255)
        draw.line((98, 42, 98, 25), fill=255)
        draw.line((98, 25, 106, 28), fill=255)

    else:
        draw.text((10, 30), "REST", font=font, fill=255)
        draw.text((90, 25), "Zzz", font=font, fill=255)

    oled.image(image)
    oled.show()


step_number = 0
play = False
first_reading = True
last_sensor_read = 0
last_status = ""
player = None

print("Starting tonearm and stepper test...")

try:
    while True:
        current_time = time.time()

        # Read the light sensor every 0.25 seconds.
        if current_time - last_sensor_read >= 0.25:
            if i2c.try_lock():
                try:
                    lux = get_light_level(i2c, ADDRESS)

                    # Ignore the first sensor reading after startup.
                    if first_reading:
                        first_reading = False
                    else:
                        play = lux >= LIGHT_THRESHOLD

                        if play:
                            print(f"{lux:.2f} lux -> PLAY")
                        else:
                            print(f"{lux:.2f} lux -> REST")

                        status = "PLAY" if play else "REST"

                        if status != last_status:
                            show_status(status)

                            if status == "PLAY":
                                player = subprocess.Popen(["pw-play", AUDIO_FILE])
                            elif player is not None:
                                player.terminate()
                                player.wait()
                                player = None

                            last_status = status

                finally:
                    i2c.unlock()

            last_sensor_read = current_time

        if play:
            # Bright LED and rotating motor in PLAY.
            led_pwm.duty_cycle = 50000

            step = steps[step_number % 4]

            for output, value in zip(outputs, step):
                output.value = value

            step_number += 1

        else:
            # Dim LED and stopped motor in REST.
            led_pwm.duty_cycle = 10000

            for output in outputs:
                output.value = False

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    if player is not None:
        player.terminate()
        player.wait()

    for output in outputs:
        output.value = False
        output.deinit()

    led_pwm.duty_cycle = 0
    led_pwm.deinit()

    oled.fill(0)
    oled.show()

    i2c.deinit()
