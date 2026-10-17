# Team Project Definition: Smart Record Player

IoT Essentials 2026 · Team: Maarten Wils, Robin Wils

## Concept

A small smart record player built around a Pico 2 W and Raspberry Pi 5. The Pico is mounted with the physical model and reads the sensors and controls the local outputs. The Pi 5 runs the player logic, Bluetooth audio, MQTT broker, ThingSpeak and AI/fallback facts.

## Information-Value Loop

| Stage | Project |
| --- | --- |
| Create | BH1750, HC-SR04, pushbutton, MCP3008 + potentiometer, RFID |
| Communicate | Pico -> MQTT over WiFi -> Mosquitto on Pi 5 |
| Analyze | player state on Pi: STANDBY / REST / PLAY / PAUSED |
| Act | Bluetooth audio, PWM LED, OLED and stepper platter |
| Dashboard / extra | ThingSpeak + AI/fallback artist facts |

## Rubric mapping

| Requirement | Implementation |
| --- | --- |
| Digital input + ultrasonic | pushbutton + HC-SR04 |
| I2C | BH1750 tonearm sensor |
| SPI analog input | MCP3008 + volume potentiometer |
| OLED | SSD1306 on SPI1 |
| Raspberry Pi | Pi 5 player, broker, audio, cloud logic |
| Raspberry Pi Pico | Pico 2 W hardware controller |
| MQTT via Pico | sensor data and commands published by Pico |
| Digital output / motor | 28BYJ-48 + ULN2003 |
| PWM | status LED |
| Online dashboard | ThingSpeak |
| AI | artist facts with fallback data |

## Current status

Most Pico hardware and the MQTT/audio flow are verified. The remaining core work is physical integration in the 3D model, final lux calibration, stepper runtime integration, final RFID record selection and final ThingSpeak/full-system verification.

## Team contribution

Both team members work on all project aspects. Maarten leads the physical prototype/integration and verification. Robin's existing Pico/Pi software contribution remains preserved; integration changes are only made where required to connect the final architecture.
