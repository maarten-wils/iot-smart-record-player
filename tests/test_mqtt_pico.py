# Test the Pico <-> Pi MQTT link without any other hardware.
#
# - prints every message the Pico sends (distance, TOGGLE, NEXT, POWER)
# - type a status + Enter to send it to the Pico:
#   PLAY -> LED on, PAUSED -> LED blinks, REST / STANDBY -> LED off
# Do not run this at the same time as record_player.py.
#
# Requires: mosquitto running on the Pi, pip install paho-mqtt

import paho.mqtt.client as mqtt

BROKER = "localhost"
TOPIC_REMOTE = "recordplayer/remote/#"
TOPIC_STATUS = "recordplayer/status"


def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to broker, waiting for the Pico...")
    client.subscribe(TOPIC_REMOTE)


def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="recordplayer-test")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)

# Network loop in a background thread, so input() below keeps working.
client.loop_start()

try:
    while True:
        status = input("Status to send (PLAY/PAUSED/REST/STANDBY): ").strip().upper()
        if status in ("PLAY", "PAUSED", "REST", "STANDBY"):
            client.publish(TOPIC_STATUS, status, retain=True)

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    client.loop_stop()
    client.disconnect()
