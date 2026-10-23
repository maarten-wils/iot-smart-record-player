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
#   PWM status LED
#   SPI OLED
#   28BYJ-48 stepper via ULN2003
#
# SPI0 is shared by MCP3008 and RC522.
# OLED uses SPI1.
# The stepper uses the same pins, sequence and 10 ms hold time
# as the verified standalone Pico test. In PLAY it runs a short
# 4-step burst, then returns to MQTT/sensor work.

import os
import time
import board
import busio
import digitalio
import pwmio
import displayio
import wifi
import socketpool

from fourwire import FourWire
import adafruit_hcsr04
import adafruit_displayio_ssd1306
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

PUBLISH_INTERVAL = 1.0
RFID_INTERVAL = 0.1
RFID_RELEASE_TIME = 0.5

BH1750_ADDRESS = 0x23

LED_FREQUENCY = 5000
LED_DIM = 10000
LED_BRIGHT = 50000

STEPPER_DELAY = 0.01
STEPPER_BURST_STEPS = 4


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


# ---------- PWM status LED ----------

status_led = pwmio.PWMOut(
    board.GP12,
    frequency=LED_FREQUENCY,
    duty_cycle=LED_DIM
)


# ---------- Stepper via ULN2003 ----------

stepper_outputs = []

for pin in (board.GP6, board.GP7, board.GP8, board.GP9):
    output = digitalio.DigitalInOut(pin)
    output.direction = digitalio.Direction.OUTPUT
    output.value = False
    stepper_outputs.append(output)

stepper_steps = [
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True)
]

stepper_index = 0
stepper_running = False


# ---------- OLED on SPI1 ----------

displayio.release_displays()

oled_spi = busio.SPI(
    board.GP10,
    MOSI=board.GP11
)

oled_bus = FourWire(
    oled_spi,
    command=board.GP13,
    chip_select=board.GP5,
    reset=board.GP22,
    baudrate=1000000
)

display = adafruit_displayio_ssd1306.SSD1306(
    oled_bus,
    width=128,
    height=64
)

oled_group = displayio.Group()
display.root_group = oled_group

oled_bitmap = displayio.Bitmap(128, 64, 1)
oled_palette = displayio.Palette(1)
oled_palette[0] = 0xFFFFFF

oled_tile = displayio.TileGrid(
    oled_bitmap,
    pixel_shader=oled_palette
)

oled_group.append(oled_tile)


player_status = "OFFLINE"
last_oled_state = None


# ---------- BH1750 ----------

i2c = busio.I2C(
    board.GP1,
    board.GP0
)

while not i2c.try_lock():
    pass

i2c.writeto(BH1750_ADDRESS, bytes([0x10]))
i2c.unlock()

time.sleep(0.2)


def read_lux():
    data = bytearray(2)

    while not i2c.try_lock():
        pass

    i2c.readfrom_into(BH1750_ADDRESS, data)
    i2c.unlock()

    value = (data[0] << 8) | data[1]
    return value / 1.2


# ---------- Shared SPI0: MCP3008 + RC522 ----------

spi = busio.SPI(
    board.GP18,
    MOSI=board.GP19,
    MISO=board.GP16
)

mcp_cs = digitalio.DigitalInOut(board.GP17)
mcp = MCP.MCP3008(spi, mcp_cs)
volume_channel = AnalogIn(mcp, MCP.P0)

rfid_cs = digitalio.DigitalInOut(board.GP20)
rfid_rst = digitalio.DigitalInOut(board.GP21)
rfid = mfrc522.MFRC522(spi, rfid_cs, rfid_rst)


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
    global player_status

    if topic != TOPIC_STATUS:
        return

    print("Status from Pi:", msg)
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
    mqtt_client._sock.settimeout(LOOP_TIMEOUT)


print("Attempting to connect to", MQTT_HOST)
mqtt_connect()


# ---------- Helpers ----------

def read_distance():
    try:
        return sonar.distance
    except RuntimeError:
        return None


def read_volume():
    return round(volume_channel.value / 65535 * 100)


def read_rfid():
    status, tag_type = rfid.request(rfid.REQALL)

    if status != rfid.OK:
        return None

    status, uid = rfid.anticoll()

    if status != rfid.OK:
        return None

    return "{:02x}{:02x}{:02x}{:02x}".format(
        uid[0], uid[1], uid[2], uid[3]
    )


def send(command):
    print("Send", command)
    mqtt_client.publish(TOPIC_COMMAND, command)


def update_stepper():
    global stepper_index, stepper_running

    if player_status != "PLAY":
        if stepper_running:
            for output in stepper_outputs:
                output.value = False
            stepper_running = False
        return

    stepper_running = True

    for _ in range(STEPPER_BURST_STEPS):
        step = stepper_steps[stepper_index]

        for output, value in zip(stepper_outputs, step):
            output.value = value

        stepper_index = (stepper_index + 1) % len(stepper_steps)
        time.sleep(STEPPER_DELAY)


def update_outputs(now):
    global last_oled_state

    if player_status == "PLAY":
        led.value = True
    elif player_status == "PAUSED":
        led.value = int(now * 2) % 2 == 0
    else:
        led.value = False

    if player_status == "PLAY":
        status_led.duty_cycle = LED_BRIGHT
    else:
        status_led.duty_cycle = LED_DIM

    if player_status == "PLAY":
        oled_state = 0
    elif player_status == "PAUSED":
        oled_state = 0 if int(now * 2) % 2 == 0 else 1
    else:
        oled_state = 1

    if oled_state != last_oled_state:
        oled_bitmap.fill(oled_state)
        last_oled_state = oled_state


# ---------- Main loop ----------

close_since = None
armed = True
pressed_since = None
long_sent = False
last_publish = 0
last_rfid_check = 0
last_rfid_uid = None
rfid_missing_since = None


while True:
    try:
        mqtt_client.loop(timeout=LOOP_TIMEOUT)
        now = time.monotonic()

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

        if not button.value:
            if pressed_since is None:
                pressed_since = now
            elif not long_sent and now - pressed_since >= LONG_PRESS:
                send("POWER")
                long_sent = True
        else:
            if pressed_since is not None:
                held = now - pressed_since
                if not long_sent and held >= DEBOUNCE:
                    send("NEXT")

            pressed_since = None
            long_sent = False

        if now - last_publish >= PUBLISH_INTERVAL:
            if distance is not None:
                mqtt_client.publish(TOPIC_DISTANCE, "%.1f" % distance)

            lux = read_lux()
            volume = read_volume()

            mqtt_client.publish(TOPIC_LUX, "%.1f" % lux)
            mqtt_client.publish(TOPIC_VOLUME, str(volume))

            print(
                "Distance:", distance,
                "| Lux:", "%.1f" % lux,
                "| Volume:", volume
            )

            last_publish = now

        if now - last_rfid_check >= RFID_INTERVAL:
            uid = read_rfid()

            if uid is not None:
                rfid_missing_since = None

                if uid != last_rfid_uid:
                    print("RFID:", uid)
                    mqtt_client.publish(TOPIC_RFID, uid)

                last_rfid_uid = uid

            elif last_rfid_uid is not None:
                if rfid_missing_since is None:
                    rfid_missing_since = now
                elif now - rfid_missing_since >= RFID_RELEASE_TIME:
                    last_rfid_uid = None
                    rfid_missing_since = None

            last_rfid_check = now

        update_stepper()
        update_outputs(now)

    except (OSError, MQTT.MMQTTException) as e:
        print("MQTT error:", e, "- reconnecting")
        led.value = False
        status_led.duty_cycle = LED_DIM
        oled_bitmap.fill(1)

        for output in stepper_outputs:
            output.value = False

        stepper_running = False
        time.sleep(2)

        try:
            mqtt_connect(reconnect=True)
        except Exception as e2:
            print("Reconnect failed:", e2)
