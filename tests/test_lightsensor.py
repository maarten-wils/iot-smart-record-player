import time
import board
import busio

# I2C1 pins on the Raspberry Pi.
scl_pin = board.D3
sda_pin = board.D2

# Start I2C communication.
i2c = busio.I2C(scl_pin, sda_pin)

# BH1750 default I2C address.
ADDRESS = 0x23

# High resolution measurement command.
COMMAND_HIGH_RES = bytearray([0x10])


def get_light_level(i2c_bus, addr):
    result = bytearray(2)

    i2c_bus.writeto_then_readfrom(
        addr,
        COMMAND_HIGH_RES,
        result
    )

    lux = ((result[0] << 8) | result[1]) / 1.2
    return lux


print("Starting BH1750 Light Sensor...")

try:
    while True:
        if i2c.try_lock():
            try:
                lux = get_light_level(i2c, ADDRESS)
                print(f"Light level: {lux:.2f} lux")
            finally:
                i2c.unlock()

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopped by user.")
