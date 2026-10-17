import time
import board
import busio
import digitalio
import mfrc522


# Shared SPI0 bus.
spi = busio.SPI(
    board.GP18,       # SCK
    MOSI=board.GP19,
    MISO=board.GP16
)


# Keep MCP3008 deselected while testing RFID.
mcp_cs = digitalio.DigitalInOut(board.GP17)
mcp_cs.switch_to_output(value=True)


# RC522 control pins.
rfid_cs = digitalio.DigitalInOut(board.GP20)
rfid_rst = digitalio.DigitalInOut(board.GP21)


# Start RFID reader.
rfid = mfrc522.MFRC522(
    spi,
    rfid_cs,
    rfid_rst
)

print("RC522 RFID test started")
print("Hold a tag near the reader")


while True:
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

            # Wait briefly so one tag does not flood the terminal.
            time.sleep(1)

    time.sleep(0.1)