# Test the ThingSpeak online dashboard without other hardware.
# Needs the ThingSpeak MQTT credentials in .env (see .env.example).
# Sends 3 updates with test values, 16 s apart (free plan limit).
# Expected: the charts on your ThingSpeak channel show the new points.
#
# Run from the repo root:  python3 tests/test_thingspeak.py

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from player import config
from player.thingspeak import ThingSpeak

thingspeak = ThingSpeak()
if not thingspeak.enabled:
    sys.exit("Fill in the THINGSPEAK_* values in .env first.")

time.sleep(2)   # give the MQTT connection a moment

test_values = [
    ("REST", 1.2, 30, 45.0, 1),
    ("PLAY", 12.5, 50, 40.0, 1),
    ("PAUSED", 12.1, 70, 6.0, 1),
]

try:
    for i, (status, lux, volume, distance, record) in enumerate(test_values, start=1):
        thingspeak.update(status=status, lux=lux, volume=volume, distance=distance, record=record)
        if i == 2:
            thingspeak.log_now_playing("Test artist", "Test record")
        thingspeak.last_sent = 0     # force sending now
        thingspeak.tick()
        print(f"update {i}/3 sent: {status}")
        if i < len(test_values):
            time.sleep(config.THINGSPEAK_INTERVAL)

    time.sleep(2)
    print(f"Done. Check https://thingspeak.mathworks.com/channels/{config.THINGSPEAK_CHANNEL_ID}")

finally:
    thingspeak.close()
