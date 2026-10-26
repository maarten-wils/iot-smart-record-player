# Testing status

Only physically verified behaviour is marked PASS.

## Pico hardware

| Test | Status | Evidence |
| --- | --- | --- |
| BH1750 I2C | PASS | changing lux values |
| HC-SR04 | PASS | changing distance + TOGGLE gesture |
| pushbutton | PASS | POWER toggles STANDBY / active player |
| MCP3008 + potentiometer | PASS | changing volume values end-to-end |
| RC522 RFID | PASS | stable UID reads for two different tags |
| MCP3008 + RC522 shared SPI0 | PASS | both work together in integrated runtime |
| PWM LED | PASS | active player bright, STANDBY dim |
| OLED SPI1 | PASS | reacts to REST / PLAY / PAUSED; blinks in PAUSED |
| 28BYJ-48 + ULN2003 stepper | PASS | platter rotates in PLAY and stops outside PLAY |
| full Pico runtime | PASS | WiFi/MQTT, sensors, RFID, OLED, PWM LED and stepper active together |

## End-to-end

| Flow | Status |
| --- | --- |
| Pico sensors -> MQTT -> Pi | PASS |
| Pi status -> MQTT -> Pico LED/OLED | PASS |
| HC-SR04 -> Pico -> MQTT TOGGLE -> PAUSED/PLAY | PASS |
| pushbutton -> Pico -> MQTT POWER -> STANDBY/active | PASS |
| MCP3008 -> Pico -> MQTT -> Pi -> Bluetooth volume | PASS |
| BH1750 -> Pico -> MQTT -> Pi REST/PLAY -> motor/audio | PASS |
| RC522 -> Pico -> MQTT UID publish | PASS |
| RFID tag 1 -> Megasong selection | PASS |
| RFID tag 2 -> Avalon selection | PASS |
| Bluetooth speaker + `pw-play` | PASS |
| ThingSpeak MQTT connection and publish | PASS |
| ThingSpeak state/lux/volume/distance/record updates | PASS |
| ThingSpeak dashboard visual check | PENDING |
| complete integrated demo in one run | PASS |

## Current calibration

`LIGHT_THRESHOLD = 4.0` lux.

Verified during the current physical setup:

- REST: approximately 0.8-1.7 lux
- PLAY: approximately 4.2 lux and higher, commonly 8-30 lux during daytime testing

The threshold may need recalibration when ambient light or the physical sensor position changes.

## RFID records

- `d5293d0a` -> Emma M. Andersson - Megasong
- `c5e63f0a` -> Al Jolson - Avalon (1920)

## Current remaining checks

- visually verify the ThingSpeak dashboard when channel access is available
- update/check remaining project documentation against the integrated runtime
- optionally improve OLED information display (state, artist/title and/or fact)
- final repo/code cleanup without changing proven functionality

## Minimal retained Pico tests

Standalone hardware tests are kept only where they still help troubleshooting. `pico/code.py` is the integrated runtime used for the final demo.
