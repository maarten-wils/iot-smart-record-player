# IoT Smart Record Player

IoT Essentials team project prototype.

## Concept

A small smart record player built around a Raspberry Pi 5. Placing the tonearm on the record
starts the platter, the music and the status display. A Pico W "gesture remote" can pause and
resume playback without touching the player, and the player's status is shared over MQTT with
an online dashboard. When a record starts, an AI model shows a short fact about the artist.

IoT Information-Value Loop:

- **create:** tonearm position (BH1750), hand gestures (HC-SR04 on the Pico), volume knob (potentiometer via MCP3008)
- **communicate:** MQTT between Pico W, Raspberry Pi and the online dashboard
- **aggregate / analyze:** play state and light level on the Pi, AI-generated artist facts
- **act:** stepper motor platter, PWM status LED, audio playback, OLED and online dashboard

## Current prototype

- Raspberry Pi 5
- 28BYJ-48 stepper motor with ULN2003
- BH1750 light sensor via I2C
- built-in PWM status LED on GPIO12
- 128x64 SSD1306 OLED via SPI1
- Bluetooth speaker with local audio playback via `pw-play`
- LEGO tonearm and enclosed record-player setup
- pushbutton kept for a later manual control function

Current behaviour:

- tonearm in REST -> low light -> motor stopped -> LED dim -> OLED shows `REST` -> audio stopped
- tonearm in PLAY -> more light -> motor rotates -> LED bright -> OLED shows `PLAY` -> audio starts
- current light threshold: 4 lux
- platter direction corrected for normal record rotation

## Planned additions

- Raspberry Pi Pico 2 W gesture remote with HC-SR04 ultrasonic sensor
- MQTT broker (Mosquitto) on the Raspberry Pi
- hand above the remote for 1 s -> MQTT `TOGGLE` -> player pauses / resumes
- player status sent back to the Pico -> onboard LED on during PLAY
- MCP3008 ADC via SPI0 with a 10k potentiometer as volume knob
- online dashboard on ThingSpeak: play state, light level, volume, now playing
- AI: short fact about the artist on the OLED and the dashboard when a record starts
- LEGO enclosure for the remote (Pico, sensor, power bank)
- role of the pushbutton (on the Pi or on the remote): to be agreed
- optional: RFID record selection (MFRC522 test in `tests/test_rfid.py`, not required for the evaluation)

Planned MQTT topics:

| Topic | Direction | Payload |
| --- | --- | --- |
| `recordplayer/remote/command` | Pico -> Pi | `TOGGLE` |
| `recordplayer/remote/distance` | Pico -> Pi / dashboard | distance in cm |
| `recordplayer/status` | Pi -> Pico / dashboard | `PLAY` / `PAUSED` / `REST` |
| `recordplayer/lux` | Pi -> dashboard | light level |

## Requirements status

| Evaluation item | Max | Covered by | Status |
| --- | ---: | --- | --- |
| Original concept / creativity | 2 | smart record player with LEGO tonearm | done |
| Digital in/out, PWM, motor, ultrasonic | 2 | stepper, PWM LED, HC-SR04 on the Pico | in progress |
| I2C | 2 | BH1750 tonearm detection | done |
| SPI: analog in, OLED | 2 | OLED via SPI1, MCP3008 + potentiometer via SPI0 | in progress |
| MQTT via Pico | 2 | Pico W gesture remote | in progress |
| Dashboard local / online | 2 | OLED, ThingSpeak | in progress |
| Extra: AI | 2 | AI artist facts | planned |
| Presentation / demo / questions | 4 | live demo, slides | planned |
| Report / video | 2 | report, YouTube demo (max 5 min) | planned |

## Task division

Every team member works on all project aspects. Specific responsibilities:

| Part | Responsible |
| --- | --- |
| Record player prototype (stepper, BH1750, PWM LED, OLED, audio) | Maarten |
| Pico W gesture remote + MQTT | Robin |
| MCP3008 ADC + volume knob | to be assigned |
| ThingSpeak online dashboard | to be assigned |
| AI artist facts | to be assigned |
| Team leader (contact with coaches, final upload on Canvas) | to be assigned |
| Documentation (report and video) | to be assigned |
| Hardware (physical setup) | to be assigned |
| Software (program structure and inline comments) | to be assigned |

## Deliverables

- [ ] Team Project Definition (one page)
- [ ] Team Project Block Schematic
- [ ] Team Project Presentation (live demo, last lesson)
- [ ] Team Project Report (incl. code, self evaluation, AI use, YouTube link)
- [ ] Buddycheck

## Connections

### Stepper motor / ULN2003

| ULN2003 | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| IN1 | GPIO17 | 11 |
| IN2 | GPIO26 | 37 |
| IN3 | GPIO27 | 13 |
| IN4 | GPIO22 | 15 |
| VCC | 5V | 2 |
| GND | GND | 6 |

### BH1750

| BH1750 | Raspberry Pi | Physical pin |
| --- | --- | ---: |
| SDA | GPIO2 / SDA1 | 3 |
| SCL | GPIO3 / SCL1 | 5 |
| VCC | 3.3V | 17 |
| GND | GND | 14 |

### PWM status LED

| LED | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| Signal | GPIO12 / PWM0 | 32 |
| GND | GND | shared GND |

### OLED display

| OLED | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| GND | GND | 39 |
| VCC | 3.3V | 1 |
| SCL | GPIO21 / SPI1 SCLK | 40 |
| SDA | GPIO20 / SPI1 MOSI | 38 |
| RES | GPIO4 | 7 |
| DC | GPIO6 | 31 |

GPIO5, GPIO18 and GPIO19 are also used by the OLED / SPI1 setup and are kept free.

### HC-SR04 on the Pico W (planned)

| HC-SR04 | Pico W | Physical pin |
| --- | --- | ---: |
| VCC | VBUS (5 V) | 40 |
| GND | GND | 38 |
| TRIG | GP2 | 4 |
| ECHO | GP3 via voltage divider (1k / 2k) | 5 |

The Pico is not wired to the Raspberry Pi; both communicate over WiFi via MQTT.

## Tests

```bash
source ~/env/bin/activate
python3 tests/test_stepper.py
python3 tests/test_button.py
python3 tests/test_lightsensor.py
python3 tests/test_oled.py
python3 tests/test_audio.py
python3 tests/test_tonearm_stepper.py
```

See `docs/setup.md` and `docs/testing.md` for the current setup and test status.

See `docs/bouwplan.md` (Dutch) for the step-by-step build plan: rebuilding the current setup and adding the Pico MQTT remote.
