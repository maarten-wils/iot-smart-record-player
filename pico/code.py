# Smart Record Player - Pico 2 W
# CircuitPython, based on Robin's working Pico MQTT remote.
#
# Existing functions kept:
#   HC-SR04: hand gesture -> TOGGLE
#   pushbutton: short press -> NEXT, long press -> POWER
#   onboard LED: player status
#   MQTT over WiFi
#
# Added hardware:
#   BH1750 light sensor
#   MCP3008 + potentiometer
#   RC522 RFID reader
#   28BYJ-48 stepper via ULN2003
#
# SPI0 is shared by MCP3008 and RC522.

import os
import time
import board
import busio
import digitalio
import wifi
import socketpool

import adafruit_hcsr04
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import mfrc522


# ---------- Settings ----------

WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_CLIENT_ID = "recordplayer-pico"

TOPIC_COMMAND = "recordplayer/remote/command"
TOPIC_DISTANCE = "recordplayer/remote/distance"
TOPIC_STATUS = "recordplayer/status"

TOPIC_LUX = "recordplayer/lux"
TOPIC_VOLUME = "recordplayer/volume"
TOPIC_RFID = "recordplayer/rfid"

TRIGGER_DISTANCE = 10
RELEASE_DISTANCE = 15
HOLD_TIME = 1.0

LONG_PRESS = 1.5
DEBOUNCE = 0.05

DISTANCE_INTERVAL = 0.05
PUBLISH_INTERVAL = 1.0

RFID_INTERVAL = 0.1
RFID_RELEASE_TIME = 0.5

BH1750_ADDRESS = 0x23

# Same timing as the standalone stepper test.
STEPPER_DELAY = 0.01

STEPPER_SEQUENCE = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
]


# ---------- HC-SR04 ----------

sonar = adafruit_hcsr04.HCSR04(
    trigger_pin=board.GP2,
    echo_pin=board.GP3,
    timeout=0.05
)


# ---------- Pushbutton ----------

button = digitalio.DigitalInOut(board.GP15)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


# ---------- Onboard status LED ----------

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

player_status = "OFFLINE"


# ---------- Stepper motor ----------

stepper_pins = [
    digitalio.DigitalInOut(board.GP6),
    digitalio.DigitalInOut(board.GP7),
    digitalio.DigitalInOut(board.GP8),
    digitalio.DigitalInOut(board.GP9),
]

for pin in stepper_pins:
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = False

stepper_index = 0
last_step = 0
stepper_running = False

# Temporary diagnostic counter.
step_count = 0


def stepper_off():
    for pin in stepper_pins:
        pin.value = False


def update_stepper(now):
    global stepper_index
    global last_step
    global stepper_running
    global step_count

    if player_status == "PLAY":
        stepper_running = True

        if now - last_step >= STEPPER_DELAY:
            pattern = STEPPER_SEQUENCE[stepper_index]

            for pin, value in zip(stepper_pins, pattern):
                pin.value = value

            stepper_index = (
                stepper_index + 1
            ) % len(STEPPER_SEQUENCE)

            last_step = now
            step_count += 1

    else:
        if stepper_running:
            stepper_off()
            stepper_running = False


# ---------- BH1750 ----------

i2c = busio.I2C(
    board.GP1,
    board.GP0
)

while not i2c.try_lock():
    pass

i2c.writeto(
    BH1750_ADDRESS,
    bytes([0x10])
)

i2c.unlock()

time.sleep(0.2)


def read_lux():
    data = bytearray(2)

    while not i2c.try_lock():
        pass

    i2c.readfrom_into(
        BH1750_ADDRESS,
        data
    )

    i2c.unlock()

    value = (data[0] << 8) | data[1]

    return value / 1.2


# ---------- Shared SPI0: MCP3008 + RC522 ----------

spi = busio.SPI(
    board.GP18,
    MOSI=board.GP19,
    MISO=board.GP16
)


# MCP3008
mcp_cs = digitalio.DigitalInOut(
    board.GP17
)

mcp = MCP.MCP3008(
    spi,
    mcp_cs
)

volume_channel = AnalogIn(
    mcp,
    MCP.P0
)


# RC522
rfid_cs = digitalio.DigitalInOut(
    board.GP20
)

rfid_rst = digitalio.DigitalInOut(
    board.GP21
)

rfid = mfrc522.MFRC522(
    spi,
    rfid_cs,
    rfid_rst
)


# ---------- WiFi ----------

print(
    "Connecting to WiFi",
    WIFI_SSID
)

wifi.radio.connect(
    WIFI_SSID,
    WIFI_PASSWORD
)

print(
    "my IP addr:",
    wifi.radio.ipv4_address
)

pool = socketpool.SocketPool(
    wifi.radio
)


# ---------- MQTT callbacks ----------

def connect(client, userdata, flags, rc):
    print(
        "Connected to MQTT broker",
        MQTT_HOST
    )

    client.subscribe(
        TOPIC_STATUS
    )


def disconnect(client, userdata, rc):
    print(
        "Disconnected from MQTT broker"
    )


def message(client, topic, msg):
    global player_status

    if topic != TOPIC_STATUS:
        return

    print(
        "Status from Pi:",
        msg
    )

    player_status = msg


CONNECT_TIMEOUT = 2
LOOP_TIMEOUT = 0.005

mqtt_client = MQTT.MQTT(
    broker=MQTT_HOST,
    port=MQTT_PORT,
    client_id=MQTT_CLIENT_ID,
    socket_pool=pool,
    is_ssl=False,
    keep_alive=60,
    socket_timeout=CONNECT_TIMEOUT,
)

mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_message = message


def mqtt_connect(reconnect=False):
    mqtt_client._socket_timeout = CONNECT_TIMEOUT

    if reconnect:
        mqtt_client.reconnect()
    else:
        mqtt_client.connect()

    mqtt_client._socket_timeout = LOOP_TIMEOUT
    mqtt_client._sock.settimeout(
        LOOP_TIMEOUT
    )


print(
    "Attempting to connect to",
    MQTT_HOST
)

mqtt_connect()


# ---------- Helpers ----------

def read_distance():
    try:
        return sonar.distance

    except RuntimeError:
        return None


def read_volume():
    return round(
        volume_channel.value
        / 65535
        * 100
    )


def read_rfid():
    status, tag_type = rfid.request(
        rfid.REQALL
    )

    if status != rfid.OK:
        return None

    status, uid = rfid.anticoll()

    if status != rfid.OK:
        return None

    return "{:02x}{:02x}{:02x}{:02x}".format(
        uid[0],
        uid[1],
        uid[2],
        uid[3]
    )


def send(command):
    print(
        "Send",
        command
    )

    mqtt_client.publish(
        TOPIC_COMMAND,
        command
    )


def update_led(now):
    if player_status == "PLAY":
        led.value = True

    elif player_status == "PAUSED":
        led.value = (
            int(now * 2) % 2 == 0
        )

    else:
        led.value = False


# ---------- Main loop ----------

close_since = None
armed = True

pressed_since = None
long_sent = False

distance = None

last_distance_read = 0
last_publish = 0

last_rfid_check = 0
last_rfid_uid = None
rfid_missing_since = None


while True:
    try:
        # MQTT
        mqtt_client.loop(
            timeout=LOOP_TIMEOUT
        )

        now = time.monotonic()

        # Stepper gets checked every loop.
        update_stepper(now)

        # --- HC-SR04 ---
        if (
            now - last_distance_read
            >= DISTANCE_INTERVAL
        ):
            distance = read_distance()
            last_distance_read = now

        # --- Gesture detection ---
        if (
            distance is not None
            and distance < TRIGGER_DISTANCE
        ):
            if close_since is None:
                close_since = now

            elif (
                armed
                and now - close_since >= HOLD_TIME
            ):
                send("TOGGLE")
                armed = False

        elif (
            distance is None
            or distance > RELEASE_DISTANCE
        ):
            close_since = None
            armed = True

        # --- Button ---
        if not button.value:
            if pressed_since is None:
                pressed_since = now

            elif (
                not long_sent
                and now - pressed_since >= LONG_PRESS
            ):
                send("POWER")
                long_sent = True

        else:
            if pressed_since is not None:
                held = now - pressed_since

                if (
                    not long_sent
                    and held >= DEBOUNCE
                ):
                    send("NEXT")

            pressed_since = None
            long_sent = False

        # --- RFID ---
        if (
            now - last_rfid_check
            >= RFID_INTERVAL
        ):
            uid = read_rfid()

            if uid is not None:
                rfid_missing_since = None

                if uid != last_rfid_uid:
                    print(
                        "RFID:",
                        uid
                    )

                    mqtt_client.publish(
                        TOPIC_RFID,
                        uid
                    )

                last_rfid_uid = uid

            elif last_rfid_uid is not None:
                if rfid_missing_since is None:
                    rfid_missing_since = now

                elif (
                    now - rfid_missing_since
                    >= RFID_RELEASE_TIME
                ):
                    last_rfid_uid = None
                    rfid_missing_since = None

            last_rfid_check = now

        # --- Periodic sensor publish ---
        if (
            now - last_publish
            >= PUBLISH_INTERVAL
        ):
            lux = read_lux()
            volume = read_volume()

            if distance is not None:
                mqtt_client.publish(
                    TOPIC_DISTANCE,
                    "%.1f" % distance
                )

            mqtt_client.publish(
                TOPIC_LUX,
                "%.1f" % lux
            )

            mqtt_client.publish(
                TOPIC_VOLUME,
                str(volume)
            )

            print(
                "Distance:",
                distance,
                "| Lux:",
                "%.1f" % lux,
                "| Volume:",
                volume,
                "| Steps/s:",
                step_count
            )

            # Start counting again for the next second.
            step_count = 0

            last_publish = now

        # --- Player status LED ---
        update_led(now)

        time.sleep(0.001)

    except (
        OSError,
        MQTT.MMQTTException
    ) as e:
        print(
            "MQTT error:",
            e,
            "- reconnecting"
        )

        led.value = False
        stepper_off()
        stepper_running = False

        time.sleep(2)

        try:
            mqtt_connect(
                reconnect=True
            )

        except Exception as e2:
            print(
                "Reconnect failed:",
                e2
            )