import time
import board
import busio
import digitalio

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import mfrc522


# -------------------------
# Shared SPI0 bus
# -------------------------

spi = busio.SPI(
    board.GP18,       # SCK
    MOSI=board.GP19,
    MISO=board.GP16
)


# -------------------------
# MCP3008
# -------------------------

mcp_cs = digitalio.DigitalInOut(board.GP17)

mcp = MCP.MCP3008(
    spi,
    mcp_cs
)

volume = AnalogIn(
    mcp,
    MCP.P0
)


# -------------------------
# RC522
# -------------------------

rfid_cs = digitalio.DigitalInOut(board.GP20)
rfid_rst = digitalio.DigitalInOut(board.GP21)

rfid = mfrc522.MFRC522(
    spi,
    rfid_cs,
    rfid_rst
)


# -------------------------
# Test
# -------------------------

print("Shared SPI test started")
print("Turn volume knob and scan RFID tag")


while True:
    # Read potentiometer through MCP3008.
    raw = volume.value
    percent = round(raw / 65535 * 100)

    print("Volume: {:3d}%".format(percent))

    # Check RFID reader.
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
            time.sleep(1)

    time.sleep(0.3)