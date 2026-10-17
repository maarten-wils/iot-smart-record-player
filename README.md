# IoT Smart Record Player

IoT Essentials team project by Maarten Wils and Robin Wils.

## Concept

A small record player in which the physical model contains the sensors and outputs. A Raspberry Pi Pico 2 W reads the hardware and communicates with a Raspberry Pi 5 over MQTT. The Pi 5 keeps the player state, audio, ThingSpeak and AI logic.

## Current architecture

**Pico 2 W in the record player**

- BH1750 light sensor (I2C) -> tonearm REST / PLAY
- HC-SR04 + pushbutton -> remote commands
- MCP3008 + 10k potentiometer (SPI0) -> volume
- RC522 RFID (shared SPI0) -> record tag
- SSD1306 OLED (SPI1) -> local status
- PWM LED -> local status
- 28BYJ-48 + ULN2003 -> platter motor; standalone verified, runtime integration still open
- WiFi + MQTT

**Raspberry Pi 5**

- Mosquitto MQTT broker
- `record_player.py` state machine
- Bluetooth audio through PipeWire
- ThingSpeak integration
- AI/fallback facts

## Verified this session

- Pico WiFi + MQTT
- HC-SR04 distance + TOGGLE command
- pushbutton short/long command
- BH1750 lux publish
- MCP3008 volume publish and end-to-end Bluetooth volume control
- RC522 tag detection + debounce
- MCP3008 and RC522 sharing SPI0
- PWM LED reacts to player status
- OLED reacts to PLAY / REST / PAUSED
- Pi receives Pico sensor data and controls Bluetooth audio
- REST / PLAY reacts to lux values

Open before final demo:

- integrate stepper smoothly into the Pico runtime
- mount hardware in the 3D model
- recalibrate REST / PLAY lux thresholds after mounting
- reconnect/test ThingSpeak credentials
- final RFID -> record selection flow
- final full-system repeatability test

## Run

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
| `recordplayer/remote/command` | Pico -> Pi | TOGGLE / NEXT / POWER |
| `recordplayer/remote/distance` | Pico -> Pi | HC-SR04 distance |
| `recordplayer/lux` | Pico -> Pi | BH1750 lux |
| `recordplayer/volume` | Pico -> Pi | MCP3008 volume % |
| `recordplayer/rfid` | Pico -> Pi | RFID UID |
| `recordplayer/status` | Pi -> Pico | STANDBY / REST / PLAY / PAUSED / OFFLINE |
| `recordplayer/now_playing` | Pi -> clients | artist / title / fact |

## Documentation

- `docs/pinout.md` - current wiring
- `docs/testing.md` - verified tests and open tests
- `docs/project-definition.md` - short project definition
- `docs/block-schematic.svg` - current architecture
- `docs/report-draft.md` - concise report draft

## Code policy

Code is kept basic and course-oriented: small steps, standalone hardware tests first, short English comments and no unnecessary abstraction.

Known exception: `pico/lib/mfrc522.py` is the explicitly approved CircuitPython RFID driver needed for the RC522.

Robin's existing contribution is preserved. Integration changes were limited to what was needed to connect the Pico-based hardware architecture to the existing Pi-side application.
