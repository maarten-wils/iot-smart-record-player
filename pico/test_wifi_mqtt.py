# Pico test 3: WiFi + MQTT only, no sensors.
# Needs settings.toml on the Pico. Copy this file to the Pico as code.py.
# Expected: on the Pi, `mosquitto_sub -h localhost -t 'recordplayer/#' -v`
# shows "recordplayer/remote/test hello N" every 2 seconds.

import os
import time
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT

print("Connecting to WiFi", os.getenv("CIRCUITPY_WIFI_SSID"))
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print("my IP addr:", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
client = MQTT.MQTT(
    broker=os.getenv("MQTT_HOST"),
    port=int(os.getenv("MQTT_PORT", 1883)),
    client_id="recordplayer-pico-test",
    socket_pool=pool,
    is_ssl=False,
)
print("Connecting to broker", os.getenv("MQTT_HOST"))
client.connect()
print("Connected!")

count = 0
while True:
    count += 1
    client.publish("recordplayer/remote/test", "hello %d" % count)
    print("sent hello", count)
    time.sleep(2)
