# Team Project Definition: Smart Record Player

IoT Essentials 2026 · Team: Maarten Wils, Robin Wils

## Concept

A small smart record player built around a Pico 2 W and Raspberry Pi 5. The Pico is mounted with the physical prototype and reads the sensors and controls the local outputs. The Pi 5 runs the player logic, Bluetooth audio, MQTT broker and ThingSpeak.

## Information-Value Loop

| Stage | Project |
| --- | --- |
| Create | BH1750, HC-SR04, pushbutton, MCP3008 + potentiometer, RFID |
| Communicate | Pico -> MQTT over WiFi -> Mosquitto on Pi 5 |
| Analyze | player state on Pi: STANDBY / REST / PLAY / PAUSED |
| Act | Bluetooth audio, PWM LED, OLED and stepper platter |
| Dashboard / extra | ThingSpeak |

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

## Current status

The integrated runtime is verified end-to-end. Lux controls REST/PLAY, the stepper platter and Bluetooth audio start/stop with player state, the potentiometer controls volume, the HC-SR04 toggles PAUSED/PLAY, the pushbutton controls STANDBY/active state, and two RFID tags select two different records. ThingSpeak MQTT connection and field updates are verified; only the visual dashboard check is still pending shared channel access.

Current calibration: `LIGHT_THRESHOLD = 4.0` lux for the present physical setup.

## Team contribution

Both team members work on the complete project. Maarten leads physical prototype integration, testing and verification. Robin's existing software contribution is preserved; integration changes are limited to what is required to connect the final architecture.
