"""MQTT link with the local broker (Mosquitto on this Pi).

Receives commands and distance from the Pico remote and publishes the
player state for the Pico and other clients. Network handling runs in
paho's background thread; commands are put in a queue that the main
loop empties, so all hardware is only touched from the main thread.
"""

import json
import queue

import paho.mqtt.client as mqtt

from . import config


class MqttLink:
    def __init__(self, client_id="recordplayer-pi"):
        self.commands = queue.Queue()
        self.distance = None   # last distance from the Pico, in cm
        self.connected = False
        self.last_status = None        # re-sent after a (re)connect
        self.last_now_playing = None

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        # "Last will": the broker publishes OFFLINE if the Pi disappears (power loss, crash).
        self.client.will_set(config.TOPIC_STATUS, "OFFLINE", retain=True)

        # connect_async + loop_start: keeps retrying if the broker is not up yet.
        self.client.connect_async(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)
        self.client.loop_start()

    # ---------- callbacks (run in the paho thread) ----------
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"[mqtt] connected to {config.MQTT_BROKER}: {reason_code}")
        self.connected = True
        client.subscribe(config.TOPIC_COMMAND)
        client.subscribe(config.TOPIC_DISTANCE)
        # Messages published before the connection was up were lost: send them again.
        if self.last_status:
            client.publish(config.TOPIC_STATUS, self.last_status, retain=True)
        if self.last_now_playing:
            client.publish(config.TOPIC_NOW_PLAYING, self.last_now_playing, retain=True)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        print(f"[mqtt] disconnected: {reason_code}")
        self.connected = False

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode(errors="ignore").strip()
        if msg.topic == config.TOPIC_COMMAND:
            print(f"[mqtt] command: {payload}")
            self.commands.put(payload)
        elif msg.topic == config.TOPIC_DISTANCE:
            try:
                self.distance = float(payload)
            except ValueError:
                pass

    # ---------- used by the main loop ----------
    def next_command(self):
        """Return the next waiting command, or None."""
        try:
            return self.commands.get_nowait()
        except queue.Empty:
            return None

    def publish_status(self, status):
        self.last_status = status
        self.client.publish(config.TOPIC_STATUS, status, retain=True)

    def publish_now_playing(self, record, fact):
        data = {"artist": record["artist"], "title": record["title"], "fact": fact}
        self.last_now_playing = json.dumps(data)
        self.client.publish(config.TOPIC_NOW_PLAYING, self.last_now_playing, retain=True)

    def publish_value(self, topic, value):
        self.client.publish(topic, str(value))

    def close(self):
        try:
            if self.connected:
                self.client.publish(config.TOPIC_STATUS, "OFFLINE", retain=True).wait_for_publish(timeout=2)
        except (RuntimeError, ValueError):
            pass   # broker already gone: the last will takes care of OFFLINE
        self.client.loop_stop()
        self.client.disconnect()
