# Test the Pico <-> Pi MQTT link without running the main application.
#
# - prints all recordplayer/* MQTT messages from the Pico and Pi
# - type a status + Enter to publish it to recordplayer/status
# - useful for checking distance, commands, lux, volume, RFID and status traffic
# Do not run this at the same time as record_player.py if you are testing status behaviour.
#
# Requires: mosquitto running on the Pi, pip install paho-mqtt

import paho.mqtt.client as mqtt

BROKER = "localhost"
TOPIC_ALL = "recordplayer/#"
TOPIC_STATUS = "recordplayer/status"


def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to broker, waiting for recordplayer messages...")
    client.subscribe(TOPIC_ALL)


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
