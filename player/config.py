"""Central configuration of the Smart Record Player.

All pins, thresholds and MQTT topics live here, so the other modules
never contain "magic numbers". Secrets (ThingSpeak, AI key) are read
from a .env file in the repo root; see .env.example.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env(path):
    """Minimal .env reader: KEY=value lines, # for comments."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env(BASE_DIR / ".env")

# ---------- Raspberry Pi pins (names of the `board` module) ----------
# Stepper motor ULN2003 IN1-IN4
STEPPER_PINS = ["D17", "D26", "D27", "D22"]
STEPPER_DELAY = 0.01       # seconds between steps (wave drive, course approach)
STEPPER_REVERSE = True     # reversed step order = correct platter direction

# BH1750 light sensor on I2C1
I2C_SCL = "D3"
I2C_SDA = "D2"
BH1750_ADDRESS = 0x23
# Temporary evening calibration: REST ~= 0.00-0.83 lux, PLAY test ~= 2.50 lux.
# Recalibrate this value in normal daylight before the final demo.
LIGHT_THRESHOLD = 2.0

# PWM status LED
LED_PIN = "D12"
LED_FREQUENCY = 5000
LED_DIM = 10000            # duty cycle in REST
LED_BRIGHT = 50000         # duty cycle in PLAY

# OLED SSD1306 on SPI1 (no physical CS pin, GPIO5 is software-only CS)
OLED_SPI = ("D21", "D20", "D19")   # SCLK, MOSI, MISO
OLED_RESET = "D4"
OLED_DC = "D6"
OLED_CS = "D5"

# MCP3008 ADC on SPI0, potentiometer on channel 0 = volume knob
ADC_SPI = ("SCLK", "MOSI", "MISO")  # GPIO11, GPIO10, GPIO9
ADC_CS = "D25"                      # GPIO25 as chip select (pin 22)
ADC_CHANNEL = 0
VOLUME_DEADBAND = 3                 # % change needed before volume is updated
# Set USE_VOLUME_KNOB=0 in .env as long as the MCP3008 is not wired yet.
USE_VOLUME_KNOB = os.getenv("USE_VOLUME_KNOB", "1") == "1"
DEFAULT_VOLUME = 20                 # safe startup volume before knob data arrives

# ---------- Audio ----------
RECORDS_FILE = BASE_DIR / "records.json"
PAUSE_MODE = os.getenv("PAUSE_MODE", "signal")   # "signal" = real pause, "restart" = stop/start

# ---------- MQTT (local broker on this Pi) ----------
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

TOPIC_COMMAND = "recordplayer/remote/command"    # Pico -> Pi: TOGGLE / POWER (NEXT is legacy/internal only)
TOPIC_DISTANCE = "recordplayer/remote/distance"  # Pico -> Pi: cm
TOPIC_STATUS = "recordplayer/status"             # Pi -> all: STANDBY / REST / PLAY / PAUSED
TOPIC_NOW_PLAYING = "recordplayer/now_playing"   # Pi -> all: JSON artist/title/fact
TOPIC_LUX = "recordplayer/lux"                   # Pico -> Pi: lux
TOPIC_VOLUME = "recordplayer/volume"             # Pico -> Pi: %
TOPIC_RFID = "recordplayer/rfid"                 # Pico -> Pi: RFID UID

# ---------- ThingSpeak (online dashboard, via MQTT like Lab 4) ----------
THINGSPEAK_HOST = os.getenv("THINGSPEAK_HOST", "mqtt3.thingspeak.com")
THINGSPEAK_PORT = int(os.getenv("THINGSPEAK_PORT", "1883"))
THINGSPEAK_CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID", "")
THINGSPEAK_CLIENT_ID = os.getenv("THINGSPEAK_CLIENT_ID", "")
THINGSPEAK_USERNAME = os.getenv("THINGSPEAK_USERNAME", "")
THINGSPEAK_PASSWORD = os.getenv("THINGSPEAK_PASSWORD", "")
THINGSPEAK_INTERVAL = float(os.getenv("THINGSPEAK_INTERVAL", "16"))  # free plan: max 1 update / 15 s

# ---------- AI artist facts ----------
AI_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_API_URL = os.getenv("AI_API_URL", "https://api.anthropic.com/v1/messages")
AI_MODEL = os.getenv("AI_MODEL", "claude-haiku-5-5")
AI_TIMEOUT = 15  # seconds

# ---------- Display ----------
FACT_PAGE_TIME = 3.0  # seconds per page when the fact is longer than the screen
