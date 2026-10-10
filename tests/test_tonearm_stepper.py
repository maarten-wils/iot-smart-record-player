import time
import board
import busio
import digitalio

# Stepper GPIO pins.
pins = [
    board.D17,
    board.D18,
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

ADDRESS = 0x23
COMMAND_HIGH_RES = bytearray([0x10])
LIGHT_THRESHOLD = 4


def get_light_level(i2c_bus, addr):
    result = bytearray(2)

    i2c_bus.writeto_then_readfrom(
        addr,
        COMMAND_HIGH_RES,
        result
    )

    return ((result[0] << 8) | result[1]) / 1.2


step_number = 0
play = False
first_reading = True
last_sensor_read = 0

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

                finally:
                    i2c.unlock()

            last_sensor_read = current_time

        if play:
            # Rotate the motor while the tonearm is in PLAY.
            step = steps[step_number % 4]

            for output, value in zip(outputs, step):
                output.value = value

            step_number += 1

        else:
            # Stop the motor in REST.
            for output in outputs:
                output.value = False

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    for output in outputs:
        output.value = False
        output.deinit()

    i2c.deinit()
