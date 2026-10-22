# Testing status

Only physically verified behaviour is marked PASS.

## Pico hardware

| Test | Status | Evidence |
| --- | --- | --- |
| BH1750 I2C | PASS | changing lux values |
| HC-SR04 | PASS | changing distance + TOGGLE command |
| pushbutton | PASS | NEXT and POWER commands |
| MCP3008 + pot | PASS | changing volume up to 100% |
| RC522 | PASS | UID read |
| MCP3008 + RC522 shared SPI0 | PASS | both work together in full runtime |
| PWM LED | PASS | PLAY bright, REST/PAUSED dim |
| OLED SPI1 | PASS | PLAY / PAUSED status reaction |
| stepper standalone | PASS | rotates with course-style wave drive |
| full Pico runtime without stepper | PASS | WiFi, MQTT, HC-SR04, button, BH1750, MCP3008, RC522, OLED and PWM LED active together |
| stepper in full Pico runtime | OPEN | MQTT timing causes poor motion |

## End-to-end

| Flow | Status |
| --- | --- |
| Pico sensors -> MQTT -> Pi | PASS |
| Pi status -> MQTT -> Pico LED/OLED | PASS |
| HC-SR04 -> Pico -> MQTT TOGGLE | PASS |
| pushbutton -> Pico -> MQTT NEXT / POWER | PASS |
| MCP3008 -> Pico -> MQTT -> Pi -> Bluetooth volume | PASS |
| BH1750 -> Pico -> MQTT -> Pi REST/PLAY -> audio | PASS |
| RC522 -> Pico -> MQTT UID publish | PASS |
| Bluetooth speaker connection + `pw-play` | PASS |
| RFID -> final record selection | OPEN |
| ThingSpeak final run | OPEN; credentials were not loaded during last test |
| full flow with stepper | OPEN |

## Current calibration

`LIGHT_THRESHOLD = 100` lux is temporary. During bench testing the sensor crossed this value easily, but values changed strongly with sensor position and ambient light.

Final REST/PLAY thresholds and possible hysteresis must be calibrated only after the BH1750 is mounted in the final physical prototype.

## Physical build status

The complete Pico hardware is currently working on one large breadboard. The next physical step is to integrate this working breadboard into the LEGO housing while keeping the wiring intact.

## Minimal retained Pico tests

- `test_bh1750_pico.py`
- `test_hcsr04.py`
- `test_button.py`
- `test_mcp3008_pico.py`
- `test_rfid_pico.py`
- `test_oled_displayio_pico.py`
- `test_pwm_led_pico.py`
- `test_stepper_pico.py`
- `test_wifi_mqtt.py`

These are standalone verification scripts. `pico/code.py` is the integrated runtime.
