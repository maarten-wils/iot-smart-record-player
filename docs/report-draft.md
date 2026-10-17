# Team Project Report: Smart Record Player

IoT Essentials 2026 · Maarten Wils / Robin Wils

> Draft. Final screenshots, self-evaluation and YouTube link are added after the final 3D integration.

## 1. Concept

The Smart Record Player combines a physical record-player model with IoT sensors, local feedback, Bluetooth audio and MQTT. The Pico 2 W handles the hardware in the model; the Raspberry Pi 5 handles the player state, audio and online services.

## 2. Information-Value Loop

| Stage | Implementation |
| --- | --- |
| Create | BH1750, HC-SR04, button, MCP3008 + potentiometer, RFID |
| Communicate | Pico 2 W -> MQTT/WiFi -> Mosquitto on Pi 5 |
| Analyze | player state: STANDBY / REST / PLAY / PAUSED |
| Act | Bluetooth audio, PWM LED, OLED, stepper motor |
| Online / extra | ThingSpeak and AI/fallback artist facts |

## 3. Architecture

![Block schematic](block-schematic.svg)

Current wiring: `pinout.md`.

## 4. Verified functionality

- BH1750 lux values from Pico over MQTT
- HC-SR04 distance and gesture command
- pushbutton NEXT / POWER commands
- MCP3008 volume potentiometer from 0-100%
- volume chain: MCP3008 -> Pico -> MQTT -> Pi -> PipeWire -> Bluetooth speaker
- RC522 RFID reading and debounce
- MCP3008 and RFID sharing SPI0
- SPI1 OLED status output
- PWM LED status output
- standalone 28BYJ-48 stepper with ULN2003
- Pi receives Pico values and starts/stops Bluetooth audio from REST/PLAY state

Detailed status: `testing.md`.

## 5. Open before final demo

- integrate the stepper into the full Pico runtime
- mount electronics in the 3D model
- calibrate final BH1750 REST/PLAY values after mounting
- connect RFID UID to final record selection
- restore and verify ThingSpeak credentials/dashboard
- repeat the complete flow several times
- add final setup photo, schematic check and demo video

## 6. Current rubric coverage

| Rubric item | Current implementation | Status |
| --- | --- | --- |
| Original concept | Smart Record Player + physical 3D model | BUILT |
| Digital in/out, PWM, motor, ultrasonic | button, HC-SR04, PWM LED, stepper | PARTLY TESTED |
| I2C | BH1750 | TESTED |
| SPI analog + OLED | MCP3008 volume + SPI OLED | TESTED |
| MQTT via Pico | live Pico publish/subscribe | TESTED |
| Local/online dashboard | OLED tested; ThingSpeak final test open | PARTLY TESTED |
| AI / extra | fallback facts work; API optional | PARTLY TESTED |
| Presentation/demo | final integrated demo still required | OPEN |
| Report/video | draft present; final evidence still required | OPEN |

## 7. Team contribution

Both team members contribute to the complete project. Maarten leads physical hardware integration, testing and current Pico hardware migration. Robin's existing software contribution is preserved; changes are only made when required for integration.

## 8. Final items to add

- team role table required by the assignment
- complete setup photo
- final schematic confirmation
- self-evaluation per rubric item with motivation
- AI-use disclosure
- YouTube demo link (max. 5 minutes)
