from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

print("RFID reader ready")
print("Place a tag on the reader...")

try:
    tag_id, text = reader.read()

    print("Tag detected!")
    print("ID:", tag_id)
    print("Text:", text.strip())

except KeyboardInterrupt:
    print("\nStopped")
