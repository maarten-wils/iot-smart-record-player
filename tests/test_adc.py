# Test the volume knob: 10k potentiometer -> MCP3008 channel 0 -> SPI0.
# Expected: turning the knob changes the value from ~0 % to ~100 %.
#
# Run from the repo root:  python3 tests/test_adc.py

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from player import config
from player.volume_knob import VolumeKnob

knob = VolumeKnob(config.ADC_SPI, config.ADC_CS, config.ADC_CHANNEL, deadband=1)

print("Turn the potentiometer. Ctrl+C to stop.")

try:
    while True:
        raw = knob.channel.value
        voltage = knob.channel.voltage
        percent, _ = knob.read()
        print(f"raw {raw:5d}   {voltage:4.2f} V   volume {percent:3d} %")
        time.sleep(0.3)

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    knob.close()
