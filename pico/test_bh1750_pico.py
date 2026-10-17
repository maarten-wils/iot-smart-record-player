import time
import board
import busio

# BH1750 connected to Pico I2C0.
i2c = busio.I2C(board.GP1, board.GP0)

ADDRESS = 0x23
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


print("Starting BH1750 on Pico...")

while True:
    if i2c.try_lock():
        try:
            lux = get_light_level(i2c, ADDRESS)
            print(f"Light level: {lux:.2f} lux")
        finally:
            i2c.unlock()

    time.sleep(1)