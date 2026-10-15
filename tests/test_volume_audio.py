# Test the volume knob together with the Bluetooth speaker.
# Plays the first record and sets the system volume from the knob.
# Expected: turning the knob makes the music louder / softer.
#
# Run from the repo root:  python3 tests/test_volume_audio.py

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from player import config
from player.audio import AudioPlayer
from player.volume_knob import VolumeKnob
from player.records import load_records

record = load_records()[0]
knob = VolumeKnob(config.ADC_SPI, config.ADC_CS, config.ADC_CHANNEL, config.VOLUME_DEADBAND)
audio = AudioPlayer()

audio.set_volume(knob.percent)
audio.play(record["path"])
print(f"Playing {record['title']}, volume {knob.percent} %. Turn the knob, Ctrl+C to stop.")

try:
    while True:
        volume, changed = knob.read()
        if changed:
            audio.set_volume(volume)
            print(f"volume -> {volume} %")
        if audio.finished():
            audio.play(record["path"])
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    audio.stop()
    knob.close()
