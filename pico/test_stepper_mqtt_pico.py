import os
import time
import board
import digitalio
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT

MQTT_HOST = os.getenv("MQTT_HOST")
TOPIC_STATUS = "recordplayer/status"

player_status = "OFFLINE"

# Stepper: same verified pins and sequence.
pins = [board.GP6, board.GP7, board.GP8, board.GP9]
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

step_index = 0

print("Connecting WiFi")
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"),
    os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
print("WiFi connected:", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)


def on_connect(client, userdata, flags, rc):
    print("MQTT connected")
    client.subscribe(TOPIC_STATUS)


def on_message(client, topic, msg):
    global player_status
    print("Status:", msg)
    player_status = msg


mqtt = MQTT.MQTT(
    broker=MQTT_HOST,
    port=1883,
    client_id="stepper-mqtt-test",
    socket_pool=pool,
    is_ssl=False,
    keep_alive=60,
    socket_timeout=2,
)

mqtt.on_connect = on_connect
mqtt.on_message = on_message
mqtt.connect()

# After connecting, use the same short socket timeout as the normal runtime.
mqtt._socket_timeout = 0.005
mqtt._sock.settimeout(0.005)

print("MQTT stepper test ready")

try:
    while True:
        mqtt.loop(timeout=0.005)

        if player_status == "PLAY":
            # Exact same 4-step block that worked in the chunk test.
            for _ in range(4):
                step = steps[step_index]

                for output, value in zip(outputs, step):
                    output.value = value

                step_index = (step_index + 1) % len(steps)
                time.sleep(0.01)
        else:
            for output in outputs:
                output.value = False

            time.sleep(0.01)

finally:
    for output in outputs:
        output.value = False
        output.deinit()
