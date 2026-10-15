# Test pause / resume of the audio without other hardware.
# Plays the first record; press Enter to pause / resume, type q + Enter to stop.
# Expected: the song pauses and continues where it stopped.
# If resuming gives glitches, set PAUSE_MODE=restart in .env.
#
# Run from the repo root:  python3 tests/test_pause_audio.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from player import config
from player.audio import AudioPlayer
from player.records import load_records

record = load_records()[0]
audio = AudioPlayer(config.PAUSE_MODE)
audio.play(record["path"])
print(f"Playing {record['title']} (pause mode: {config.PAUSE_MODE})")

try:
    while True:
        answer = input("Enter = pause/resume, q = quit: ").strip().lower()
        if answer == "q":
            break
        if audio.paused:
            audio.resume()
            print("RESUME")
        else:
            audio.pause()
            print("PAUSE")

except KeyboardInterrupt:
    print()

finally:
    audio.stop()
    print("STOP")
