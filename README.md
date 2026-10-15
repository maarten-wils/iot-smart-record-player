# IoT Smart Record Player

IoT Essentials team project prototype.

## Concept

A small smart record player built around a Raspberry Pi 5. Placing the tonearm on the record
starts the platter, the music and the status display. A wireless Pico 2 W remote pauses and
resumes playback with a hand gesture, selects the next record and switches the player to
standby. The player's status is shared over MQTT with the remote and with an online
ThingSpeak dashboard. When a record is selected, an AI model shows a short fact about the artist.

IoT Information-Value Loop:

- **create:** tonearm position (BH1750), volume knob (potentiometer via MCP3008), hand gestures (HC-SR04) and button on the Pico remote
- **communicate:** MQTT between the Pico remote, the Mosquitto broker on the Pi and ThingSpeak
- **aggregate / analyze:** player state machine on the Pi, AI-generated artist facts
- **act:** stepper motor platter, PWM status LED, audio playback, OLED, LED on the remote, online dashboard

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

## Full application (`record_player.py`)

Code ready and tested in simulation; to be tested on the real hardware.

- Pico 2 W remote with HC-SR04 and pushbutton, MQTT over WiFi
  - hand above the remote for 1 s -> `TOGGLE` -> pause / resume (real pause, the song continues)
  - short button press -> `NEXT` -> next record
  - long button press (1.5 s) -> `POWER` -> standby on / off
  - onboard LED: on in PLAY, blinking in PAUSED
- Mosquitto MQTT broker on the Raspberry Pi
- stepper motor in its own thread (smooth platter while the rest of the program runs)
- PWM LED: off in standby, dim in REST, bright in PLAY, breathing in PAUSED
- MCP3008 ADC via SPI0 with a 10k potentiometer as volume knob
- OLED: status, volume, artist, title and the AI fact
- ThingSpeak online dashboard via MQTT: play state, light, volume, remote distance, record, "Now playing" history
- AI: short fact about the artist (Claude API), with fallback facts in `records.json`
- records and audio files listed in `records.json`

MQTT topics:

| Topic | Direction | Payload |
| --- | --- | --- |
| `recordplayer/remote/command` | Pico -> Pi | `TOGGLE` / `NEXT` / `POWER` |
| `recordplayer/remote/distance` | Pico -> Pi | distance in cm |
| `recordplayer/status` | Pi -> Pico, others | `STANDBY` / `REST` / `PLAY` / `PAUSED` / `OFFLINE` |
| `recordplayer/now_playing` | Pi -> others | JSON artist / title / fact |
| `recordplayer/lux` | Pi -> others | light level |
| `recordplayer/volume` | Pi -> others | volume % |

## Requirements status

| Evaluation item | Max | Covered by | Status |
| --- | ---: | --- | --- |
| Original concept / creativity | 2 | smart record player with LEGO tonearm and gesture remote | done |
| Digital in/out, PWM, motor, ultrasonic | 2 | stepper, PWM LED, HC-SR04 + button on the Pico | code ready |
| I2C | 2 | BH1750 tonearm detection | done |
| SPI: analog in, OLED | 2 | OLED via SPI1, MCP3008 + potentiometer via SPI0 | code ready |
| MQTT via Pico | 2 | Pico 2 W remote | code ready |
| Dashboard local / online | 2 | OLED, ThingSpeak | code ready |
| Extra: AI | 2 | AI artist facts | code ready |
| Presentation / demo / questions | 4 | live demo, slides | planned |
| Report / video | 2 | report, YouTube demo (max 5 min) | draft |

## Task division

Every team member works on all project aspects. Specific responsibilities:

| Part | Responsible |
| --- | --- |
| Record player prototype (stepper, BH1750, PWM LED, OLED, audio) | Maarten |
| Pico 2 W remote + MQTT | Robin |
| MCP3008 ADC + volume knob | Robin |
| ThingSpeak online dashboard | Robin |
| AI artist facts | Robin |
| Full application (`record_player.py`, `player/`) | Robin |
| Team leader (contact with coaches, final upload on Canvas) | to be agreed |
| Documentation (report and video) | to be agreed |
| Hardware (physical setup) | to be agreed |
| Software (program structure and inline comments) | to be agreed |

## Deliverables

- [ ] Team Project Definition (one page) - draft in `docs/project-definition.md`
- [ ] Team Project Block Schematic - `docs/block-schematic.svg`
- [ ] Team Project Presentation (live demo, last lesson)
- [ ] Team Project Report (incl. code, self evaluation, AI use, YouTube link) - draft in `docs/report-draft.md`
- [ ] Buddycheck

## Project structure

```
record_player.py         main program on the Raspberry Pi
records.json             records: audio file, artist, title, fallback facts
.env.example             settings and keys (copy to .env, never commit .env)
requirements.txt         Python packages for the Pi
player/
  config.py              all pins, thresholds, MQTT topics
  state.py               player state machine (STANDBY / REST / PLAY / PAUSED)
  stepper.py             platter motor in its own thread
  light_sensor.py        BH1750 tonearm detection (I2C)
  status_led.py          PWM status LED
  display.py             OLED local dashboard (SPI1)
  volume_knob.py         potentiometer via MCP3008 (SPI0)
  audio.py               playback, pause, volume (PipeWire)
  mqtt_link.py           local MQTT broker link (Pico remote)
  thingspeak.py          online dashboard (ThingSpeak MQTT)
  ai_facts.py            AI artist facts
  records.py             loads records.json
pico/
  code.py                the Pico remote
  settings.toml.example  WiFi + broker IP (copy to the Pico as settings.toml)
  test_*.py              Pico tests (copy to the Pico as code.py)
tests/                   one test per part, see docs/bouwplan.md
docs/
  bouwplan.md            step-by-step build and test plan (Dutch)
  pinout.md              all connections in one place
  pico-mqtt.md           remote behaviour and MQTT topics
  setup.md, testing.md   original prototype setup and test status
```

## Connections

All connections, including the MCP3008 and the Pico remote: see `docs/pinout.md`.

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

### MCP3008 ADC (SPI0)

| MCP3008 | Raspberry Pi | Physical pin |
| --- | --- | ---: |
| VDD (16), VREF (15) | 3.3V | 17 (via rail) |
| AGND (14), DGND (9) | GND | 25 (via rail) |
| CLK (13) | GPIO11 / SPI0 SCLK | 23 |
| DOUT (12) | GPIO9 / SPI0 MISO | 21 |
| DIN (11) | GPIO10 / SPI0 MOSI | 19 |
| CS (10) | GPIO25 | 22 |
| CH0 (1) | potentiometer wiper | – |

### Pico 2 W remote

| Part | Pico | Physical pin |
| --- | --- | ---: |
| HC-SR04 VCC | VBUS (5 V) | 40 |
| HC-SR04 GND | GND | 38 |
| HC-SR04 TRIG | GP2 | 4 |
| HC-SR04 ECHO | GP3 via voltage divider (1k / 2k) | 5 |
| button | GP15 + GND (internal pull-up) | 20, 18 |

The Pico is not wired to the Raspberry Pi; both communicate over WiFi via MQTT.

## Run

```bash
cd ~/iot-smart-record-player
source ~/env/bin/activate
cp .env.example .env      # first time only, then fill in
python3 record_player.py
```

## Tests

```bash
source ~/env/bin/activate
python3 tests/test_stepper.py
python3 tests/test_button.py
python3 tests/test_lightsensor.py
python3 tests/test_oled.py
python3 tests/test_audio.py
python3 tests/test_tonearm_stepper.py
python3 tests/test_pause_audio.py
python3 tests/test_adc.py
python3 tests/test_volume_audio.py
python3 tests/test_mqtt_pico.py
python3 tests/test_thingspeak.py
python3 tests/test_ai_fact.py
python3 tests/test_state.py        # logic only, runs on any computer
```

See `docs/setup.md` and `docs/testing.md` for the original setup and test status.

See `docs/bouwplan.md` (Dutch) for the step-by-step build plan.
