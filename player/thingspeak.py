"""Online dashboard: ThingSpeak via MQTT (same method as Lab 4).

Channel fields:
    field1  play state   0 = standby, 1 = rest, 2 = paused, 3 = play
    field2  light level  lux
    field3  volume       %
    field4  distance     cm (from the Pico remote)
    field5  record       number of the selected record (1, 2, ...)
    status  "Now playing: <artist> - <title>"  -> history of played records

The free ThingSpeak plan accepts one update per 15 seconds, so values are
collected and sent at most every THINGSPEAK_INTERVAL seconds.
"""

import time
from urllib.parse import quote

import paho.mqtt.client as mqtt

from . import config

STATE_CODES = {"STANDBY": 0, "REST": 1, "PAUSED": 2, "PLAY": 3}


class ThingSpeak:
    def __init__(self):
        self.enabled = all([
            config.THINGSPEAK_CHANNEL_ID,
            config.THINGSPEAK_CLIENT_ID,
            config.THINGSPEAK_USERNAME,
            config.THINGSPEAK_PASSWORD,
        ])
        self.fields = {}
        self.status_text = None
        self.dirty = False
        self.last_sent = 0
        self.client = None

        if not self.enabled:
            print("[thingspeak] no credentials in .env -> online dashboard disabled")
            return

        self.topic = f"channels/{config.THINGSPEAK_CHANNEL_ID}/publish"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=config.THINGSPEAK_CLIENT_ID)
        self.client.username_pw_set(config.THINGSPEAK_USERNAME, config.THINGSPEAK_PASSWORD)
        self.client.on_connect = lambda c, u, f, rc, p: print(f"[thingspeak] connected: {rc}")
        self.client.connect_async(config.THINGSPEAK_HOST, config.THINGSPEAK_PORT, keepalive=60)
        self.client.loop_start()

    def update(self, status=None, lux=None, volume=None, distance=None, record=None):
        """Store new values; they are sent on the next allowed moment."""
        new = {
            "field1": STATE_CODES.get(status) if status else None,
            "field2": round(lux, 1) if lux is not None else None,
            "field3": volume,
            "field4": round(distance, 1) if distance is not None else None,
            "field5": record,
        }
        for key, value in new.items():
            if value is not None and self.fields.get(key) != value:
                self.fields[key] = value
                self.dirty = True

    def log_now_playing(self, artist, title):
        """Status messages build the 'played records' history on ThingSpeak."""
        self.status_text = f"Now playing: {artist} - {title}"
        self.dirty = True

    def tick(self):
        """Call from the main loop; sends when allowed and something changed."""
        if not self.enabled or not self.dirty:
            return
        now = time.monotonic()
        if now - self.last_sent < config.THINGSPEAK_INTERVAL:
            return

        payload = "&".join(f"{key}={value}" for key, value in sorted(self.fields.items()))
        if self.status_text:
            payload += "&status=" + quote(self.status_text)
            self.status_text = None

        self.client.publish(self.topic, payload)
        print(f"[thingspeak] sent {payload}")
        self.last_sent = now
        self.dirty = False

    def close(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
