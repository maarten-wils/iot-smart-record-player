import math
import os
import struct
import subprocess
import wave

AUDIO_FILE = "/tmp/audio_test.wav"
SAMPLE_RATE = 44100
DURATION = 20
FREQUENCY = 440

# Create a simple temporary test tone.
with wave.open(AUDIO_FILE, "w") as audio:
    audio.setnchannels(1)
    audio.setsampwidth(2)
    audio.setframerate(SAMPLE_RATE)

    for i in range(SAMPLE_RATE * DURATION):
        value = int(8000 * math.sin(2 * math.pi * FREQUENCY * i / SAMPLE_RATE))
        audio.writeframes(struct.pack("<h", value))

print("PLAY")
player = subprocess.Popen(["pw-play", AUDIO_FILE])

input("Press Enter to STOP... ")

player.terminate()
player.wait()

os.remove(AUDIO_FILE)
print("STOP")
