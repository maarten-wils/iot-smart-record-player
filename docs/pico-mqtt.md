# Pico remote + MQTT

The Pico 2 W is a wireless remote for the record player. It is not wired to the
Raspberry Pi; both talk over WiFi via MQTT, through the Mosquitto broker on the Pi.

| On the remote | What happens |
| --- | --- |
| hand < 10 cm above the HC-SR04 for 1 s | `TOGGLE`: pause / resume |
| short press on the button | `NEXT`: next record (new AI fact) |
| long press (1.5 s) on the button | `POWER`: standby on / off |
| onboard LED | on = PLAY, blinking = PAUSED, off = REST / STANDBY / Pi offline |

Wiring: see [pinout.md](pinout.md). Build and test steps: see [bouwplan.md](bouwplan.md), part 2.

## MQTT topics

| Topic | Direction | Payload |
| --- | --- | --- |
| `recordplayer/remote/command` | Pico -> Pi | `TOGGLE` / `NEXT` / `POWER` |
| `recordplayer/remote/distance` | Pico -> Pi | distance in cm, every 1 s |
| `recordplayer/status` | Pi -> Pico, others | `STANDBY` / `REST` / `PLAY` / `PAUSED` / `OFFLINE` (retained) |
| `recordplayer/now_playing` | Pi -> others | JSON `{"artist", "title", "fact"}` (retained) |
| `recordplayer/lux` | Pi -> others | light level, every 2 s |
| `recordplayer/volume` | Pi -> others | volume %, every 2 s and on change |

`OFFLINE` is the Pi's MQTT "last will": the broker publishes it when the Pi
program stops or loses its connection.

Watch everything live on the Pi:

```bash
mosquitto_sub -h localhost -t 'recordplayer/#' -v
```

Send a command by hand (without the Pico):

```bash
mosquitto_pub -h localhost -t recordplayer/remote/command -m TOGGLE
```

## Files on the Pico

| File | Purpose |
| --- | --- |
| `pico/code.py` | the remote (copy to the Pico as `code.py`) |
| `pico/settings.toml.example` | WiFi + broker IP (copy as `settings.toml`, never commit) |
| `pico/test_hcsr04.py` | test 1: sensor only |
| `pico/test_button.py` | test 2: button only |
| `pico/test_wifi_mqtt.py` | test 3: WiFi + MQTT only |

To run a test, copy it to the Pico **as `code.py`** (CircuitPython always runs `code.py`).
