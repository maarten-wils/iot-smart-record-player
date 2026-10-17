import board
import busio

print("Starting Pico SPI test...")

spi = busio.SPI(
    board.GP18,
    MOSI=board.GP19
)

if spi.try_lock():
    print("SPI lock OK")

    spi.configure(
        baudrate=500000,
        polarity=0,
        phase=0
    )

    print("SPI configured OK")
    spi.unlock()

print("SPI test finished")