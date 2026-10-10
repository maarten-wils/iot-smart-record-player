import time
import board
import busio

# I2C1 pins on the Raspberry Pi.
scl_pin = board.D3
sda_pin = board.D2

# Start I2C communication.
i2c = busio.I2C(scl_pin, sda_pin)

# BH1750 settings.
ADDRESS = 0x23
COMMAND_HIGH_RES = bytearray([0x10])

# Threshold based on measured REST and PLAY values.
LIGHT_THRESHOLD = 10


def get_light_level(i2c_bus, addr):
    result = bytearray(2)

    i2c_bus.writeto_then_readfrom(
        addr,
        COMMAND_HIGH_RES,
        result
    )

    lux = ((result[0] << 8) | result[1]) / 1.2
    return lux


print("Starting tonearm test...")

first_reading = True

try:
    while True:
        if i2c.try_lock():
            try:
                lux = get_light_level(i2c, ADDRESS)

                # Ignore the first sensor reading after startup.
                if first_reading:
                    first_reading = False
                else:
                    if lux < LIGHT_THRESHOLD:
                        print(f"{lux:.2f} lux -> PLAY")
                    else:
                        print(f"{lux:.2f} lux -> REST")

            finally:
                i2c.unlock()

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopped by user.")
