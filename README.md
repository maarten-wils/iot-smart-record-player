# IoT Smart Record Player

IoT Essentials team project by Maarten Wils and Robin Wils.

## Concept

A small record player in which the physical model contains the sensors and outputs. A Raspberry Pi Pico 2 W reads the hardware and communicates with a Raspberry Pi 5 over MQTT. The Pi 5 keeps the player state, audio and ThingSpeak integration.

## Current architecture

**Pico 2 W in the record player**

- BH1750 light sensor (I2C) -> tonearm REST / PLAY
- HC-SR04 + pushbutton -> remote commands
- MCP3008 + 10k potentiometer (SPI0) -> volume
- RC522 RFID (shared SPI0) -> record tag
- SSD1306 OLED (SPI1) -> local status + current artist/title
- PWM LED -> local player status
- 28BYJ-48 + ULN2003 -> platter motor
- WiFi + MQTT

**Raspberry Pi 5**

- Mosquitto MQTT broker
- `record_player.py` state machine
- Bluetooth audio through PipeWire
- ThingSpeak integration

## Verified integrated behaviour

The complete runtime has been verified in end-to-end testing:

- Pico WiFi + MQTT
- BH1750 REST / PLAY detection
- HC-SR04 TOGGLE gesture for PLAY / PAUSED
- pushbutton POWER for STANDBY / active player
- MCP3008 volume -> MQTT -> Pi -> Bluetooth speaker
- RC522 RFID selection for two different records
- OLED shows REST / PLAY / PAUSE / OFF and current artist/title in PLAY/PAUSE
- PWM LED is bright while active and dim in STANDBY
- stepper platter runs in PLAY and stops outside PLAY
- Bluetooth audio starts/stops/pauses/resumes with player state
- ThingSpeak MQTT connection and field updates
- full integrated demo completed in one run and recorded on video

Current RFID mappings:

- `d5293d0a` -> Emma M. Andersson - Megasong
- `c5e63f0a` -> Al Jolson - Avalon (1920)

Current BH1750 threshold:

- `LIGHT_THRESHOLD = 4.0`
- REST observed around 0.8-1.7 lux
- PLAY observed from about 4.2 lux upward in the current setup

## Remaining work

- visually verify the ThingSpeak dashboard when channel access is available
- review/finalize report, setup photo, schematic and self-evaluation
- optional physical/LEGO finishing if time remains

## Run

Pico dependency for OLED text:

- `adafruit_display_text` from the matching CircuitPython 10.x library bundle must be present under `CIRCUITPY/lib`.
- On the current Pi this was copied from `~/Downloads/circuitpy-bundle/adafruit-circuitpython-bundle-10.x-mpy-20261010/lib/adafruit_display_text`.

Pico:

```bash
cp pico/code.py /media/mwi/CIRCUITPY/code.py
sync
```

Pi:

```bash
cd ~/iot-smart-record-player
source ~/env/bin/activate
python3 record_player.py
```

Bluetooth check:

```bash
bluetoothctl info 2C:FD:B4:50:CA:94
wpctl status
```

## MQTT topics

| Topic | Direction | Purpose |
| --- | --- | --- |
| `recordplayer/remote/command` | Pico -> Pi | TOGGLE / POWER |
| `recordplayer/remote/distance` | Pico -> Pi | HC-SR04 distance |
| `recordplayer/lux` | Pico -> Pi | BH1750 lux |
| `recordplayer/volume` | Pico -> Pi | MCP3008 volume % |
| `recordplayer/rfid` | Pico -> Pi | RFID UID / record selection |
| `recordplayer/status` | Pi -> Pico | STANDBY / REST / PLAY / PAUSED / OFFLINE |
| `recordplayer/now_playing` | Pi -> clients | artist / title |

`NEXT` is still accepted internally by the state machine for compatibility/testing, but the current Pico does not send it. Record selection in the final setup is done through RFID.

## Record Library app (optional)

The [Record Library app](https://github.com/r-wils/record-library-app) links new RFID tags to audio files from a laptop. It copies the audio to `audio/` on the Pi and writes `audio/library.json`. The player reads those records next to `records.json` and reloads them within 2 seconds after a change, without a restart. A library record with the same tag as a `records.json` record replaces it. Without `library.json` the player only uses `records.json`. `audio/` is in `.gitignore`, so music and the library never end up in git.

Test without hardware: `python3 tests/test_records.py`

## Documentation

- `docs/pinout.md` - current wiring
- `docs/testing.md` - physically verified tests and remaining checks
- `docs/project-definition.md` - short project definition
- `docs/block-schematic.svg` - current architecture
- `docs/report-draft.md` - concise report draft
- `docs/todo.md` - remaining project work

## Code policy

Code is kept basic and course-oriented: small steps, standalone hardware tests first, short English comments and no unnecessary abstraction.

Known exception: `pico/lib/mfrc522.py` is the explicitly approved CircuitPython RFID driver needed for the RC522. The OLED text uses the standard `adafruit_display_text` folder from the CircuitPython library bundle installed on the Pico.

Robin's existing contribution is preserved. Integration changes were limited to what was needed to connect the Pico-based hardware architecture to the existing Pi-side application.
