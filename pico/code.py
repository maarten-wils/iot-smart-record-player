# Smart Record Player - Pico 2 W remote
# CircuitPython, based on the course example PicoW_MQTT_v0.py
#
# Inputs:
#   HC-SR04 ultrasonic sensor: hand < 10 cm for 1 s -> TOGGLE (pause / resume)
#   pushbutton: short press -> NEXT (next record), long press (1.5 s) -> POWER (standby on/off)
# Output:
#   onboard LED: on = PLAY, blinking = PAUSED, off = REST / STANDBY / Pi offline
# Communication:
#   MQTT over WiFi with the broker (Mosquitto) on the Raspberry Pi
#
# Libraries needed in /lib on the Pico (CircuitPython bundle):
#   adafruit_minimqtt, adafruit_connection_manager, adafruit_hcsr04, adafruit_ticks

import os
import time
import board
import digitalio
import wifi
import socketpool
import adafruit_hcsr04
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# ---------- Settings ----------
# WiFi and broker come from settings.toml (see settings.toml.example)
WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
MQTT_HOST = os.getenv("MQTT_HOST")          # IP address of the Raspberry Pi
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_CLIENT_ID = "recordplayer-pico"

TOPIC_COMMAND = "recordplayer/remote/command"    # Pico -> Pi
TOPIC_DISTANCE = "recordplayer/remote/distance"  # Pico -> Pi / dashboard
TOPIC_STATUS = "recordplayer/status"             # Pi -> Pico

TRIGGER_DISTANCE = 10    # cm: hand closer than this counts as a gesture
RELEASE_DISTANCE = 15    # cm: hand must move further than this to re-arm
HOLD_TIME = 1.0          # s: how long the hand must stay close
LONG_PRESS = 1.5         # s: button held this long = POWER
DEBOUNCE = 0.05          # s: ignore button bounces shorter than this
PUBLISH_INTERVAL = 1.0   # s: distance publish period

# ---------- Hardware ----------
# HC-SR04: TRIG on GP2, ECHO on GP3 (through a voltage divider, ECHO is 5 V!)
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP2, echo_pin=board.GP3, timeout=0.05)

# Pushbutton between GP15 and GND, internal pull-up: released = True, pressed = False
button = digitalio.DigitalInOut(board.GP15)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Onboard LED shows the player status
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

player_status = "OFFLINE"

# ---------- WiFi ----------
print("Connecting to WiFi", WIFI_SSID)
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print("my IP addr:", wifi.radio.ipv4_address)
pool = socketpool.SocketPool(wifi.radio)


# ---------- MQTT callbacks ----------
def connect(client, userdata, flags, rc):
    print("Connected to MQTT broker", MQTT_HOST)
    client.subscribe(TOPIC_STATUS)


def disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker")


def message(client, topic, msg):
    # The Pi publishes STANDBY / REST / PLAY / PAUSED (or OFFLINE)
    global player_status
    if topic != TOPIC_STATUS:
        return
    print("Status from Pi:", msg)
    player_status = msg


CONNECT_TIMEOUT = 2     # s: setting up the connection over WiFi needs time
LOOP_TIMEOUT = 0.05     # s: afterwards short timeouts keep sensor + button responsive

mqtt_client = MQTT.MQTT(
    broker=MQTT_HOST,
    port=MQTT_PORT,
    client_id=MQTT_CLIENT_ID,
    socket_pool=pool,
    is_ssl=False,          # local broker, no TLS
    keep_alive=60,
    socket_timeout=CONNECT_TIMEOUT,
)
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_message = message


def mqtt_connect(reconnect=False):
    """Connect with a long timeout, then switch to a short one for the main loop."""
    mqtt_client._socket_timeout = CONNECT_TIMEOUT
    if reconnect:
        mqtt_client.reconnect()
    else:
        mqtt_client.connect()
    mqtt_client._socket_timeout = LOOP_TIMEOUT
    mqtt_client._sock.settimeout(LOOP_TIMEOUT)


print("Attempting to connect to", MQTT_HOST)
mqtt_connect()


# ---------- Helpers ----------
def read_distance():
    """Return distance in cm, or None if the sensor timed out."""
    try:
        return sonar.distance
    except RuntimeError:
        # No echo received (nothing in range) - not an error for us
        return None


def send(command):
    print("Send", command)
    mqtt_client.publish(TOPIC_COMMAND, command)


def update_led(now):
    if player_status == "PLAY":
        led.value = True
    elif player_status == "PAUSED":
        led.value = int(now * 2) % 2 == 0   # blink twice per second
    else:
        led.value = False


# ---------- Main loop ----------
close_since = None     # time when the hand came close
armed = True           # False after a gesture until the hand is removed
pressed_since = None   # time when the button went down
long_sent = False      # POWER already sent for this press
last_publish = 0

while True:
    try:
        # Handle incoming messages (status from the Pi)
        mqtt_client.loop(timeout=LOOP_TIMEOUT)

        now = time.monotonic()

        # --- Gesture detection with hysteresis ---
        distance = read_distance()
        if distance is not None and distance < TRIGGER_DISTANCE:
            if close_since is None:
                close_since = now
            elif armed and now - close_since >= HOLD_TIME:
                send("TOGGLE")
                armed = False
        elif distance is None or distance > RELEASE_DISTANCE:
            close_since = None
            armed = True

        # --- Button: short press = NEXT, long press = POWER ---
        if not button.value:                       # pressed
            if pressed_since is None:
                pressed_since = now
            elif not long_sent and now - pressed_since >= LONG_PRESS:
                send("POWER")
                long_sent = True
        else:                                      # released
            if pressed_since is not None:
                held = now - pressed_since
                if not long_sent and held >= DEBOUNCE:
                    send("NEXT")
            pressed_since = None
            long_sent = False

        # --- Periodic distance publish for the dashboard ---
        if now - last_publish >= PUBLISH_INTERVAL:
            if distance is not None:
                mqtt_client.publish(TOPIC_DISTANCE, "%.1f" % distance)
            last_publish = now

        update_led(now)
        time.sleep(0.02)

    except (OSError, MQTT.MMQTTException) as e:
        # WiFi or broker hiccup: wait and reconnect
        print("MQTT error:", e, "- reconnecting")
        led.value = False
        time.sleep(2)
        try:
            mqtt_connect(reconnect=True)
        except Exception as e2:
            print("Reconnect failed:", e2)
