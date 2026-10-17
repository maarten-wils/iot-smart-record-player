import os
import time
import board
import digitalio
import wifi
import socketpool

import adafruit_minimqtt.adafruit_minimqtt as MQTT


# ---------- Stepper ----------

pins = [
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9
]

outputs = []

for pin in pins:
    output = digitalio.DigitalInOut(pin)
    output.direction = digitalio.Direction.OUTPUT
    outputs.append(output)


steps = [
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True)
]


# ---------- WiFi / MQTT ----------

WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

TOPIC_STATUS = "recordplayer/status"

CONNECT_TIMEOUT = 2
LOOP_TIMEOUT = 0.001

player_status = "OFFLINE"


print("Connecting to WiFi")

wifi.radio.connect(
    WIFI_SSID,
    WIFI_PASSWORD
)

print("WiFi connected")

pool = socketpool.SocketPool(
    wifi.radio
)


def connect(client, userdata, flags, rc):
    print("MQTT connected")
    client.subscribe(TOPIC_STATUS)


def message(client, topic, msg):
    global player_status

    if topic == TOPIC_STATUS:
        player_status = msg
        print("Status:", player_status)


mqtt_client = MQTT.MQTT(
    broker=MQTT_HOST,
    port=MQTT_PORT,
    client_id="stepper-mqtt-test",
    socket_pool=pool,
    is_ssl=False,
    socket_timeout=CONNECT_TIMEOUT
)

mqtt_client.on_connect = connect
mqtt_client.on_message = message

mqtt_client.connect()

# Same approach as Robin's working MQTT code:
# short socket timeout after connection.
mqtt_client._socket_timeout = LOOP_TIMEOUT
mqtt_client._sock.settimeout(LOOP_TIMEOUT)


# ---------- Main loop ----------

step_number = 0

print("Stepper + MQTT test started")


while True:
    mqtt_client.loop(
        timeout=LOOP_TIMEOUT
    )

    if player_status == "PLAY":
        step = steps[
            step_number % 4
        ]

        for output, value in zip(
            outputs,
            step
        ):
            output.value = value

        step_number += 1

        # Exact timing from working standalone test.
        time.sleep(0.01)

    else:
        for output in outputs:
            output.value = False

        time.sleep(0.01)