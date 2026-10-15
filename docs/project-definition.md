# Team Project Definition: Smart Record Player

IoT Essentials 2026 · Team: Maarten Wils, Robin Wils

## What will we make?

A small smart record player. Placing the (LEGO) tonearm on the record starts the
platter, the music and the status display; lifting it stops everything. A separate
wireless remote pauses the music with a hand gesture, selects the next record and
switches the player to standby. The player status is visible on an OLED, on the remote
and on an online dashboard. For every record an AI model shows a short fun fact about the artist.

## Added value

The project turns a nostalgic, purely mechanical object into a connected device:
contact-free control, remote monitoring of what is playing, and extra context about
the music, while keeping the familiar "tonearm on the record" interaction.

## IoT Information-Value Loop

| Stage | In our project |
| --- | --- |
| Create | BH1750 light sensor (tonearm position), potentiometer via MCP3008 (volume), HC-SR04 and pushbutton on the Pico remote |
| Communicate | MQTT over WiFi between the Pico and the Mosquitto broker on the Pi; MQTT to ThingSpeak; HTTPS to the AI |
| Aggregate | the Pi combines tonearm, remote commands and volume into one player state |
| Analyze | state machine (standby / rest / play / paused); AI generates an artist fact |
| Act | stepper motor platter, PWM LED, audio, OLED, LED on the remote, ThingSpeak dashboard |

## How we meet the requirements

| Requirement | Solution |
| --- | --- |
| Digital input (incl. ultrasonic) | HC-SR04 gesture sensor and pushbutton on the Pico |
| I2C sensor | BH1750 light sensor detects the tonearm |
| SPI (analog input via ADC) | 10k potentiometer via MCP3008 on SPI0 as volume knob |
| Raspberry Pi | Pi 5 runs the player, the MQTT broker and the dashboards |
| Raspberry Pi Pico | Pico 2 W as wireless remote (CircuitPython) |
| MQTT | Pico <-> Mosquitto broker on the Pi; Pi -> ThingSpeak |
| Online dashboard | ThingSpeak channel: play state, light, volume, distance, now playing |
| Local dashboard (OLED) | SSD1306 OLED via SPI1: status, volume, artist, title, AI fact |
| AI | Claude API generates a fun fact about the artist of each record |
| Digital output incl. motor | 28BYJ-48 stepper motor via ULN2003 turns the platter |
| PWM | status LED: dim, bright or "breathing" depending on the state |

## Team and responsibilities

Both team members work on all aspects of the project. Specific responsibilities:

| Role | Responsible |
| --- | --- |
| Team leader (contact with coaches, upload on Canvas) | [to be agreed] |
| Documentation (report and video) | [to be agreed] |
| Hardware (physical setup) | Maarten: record player prototype and LEGO build |
| Software (program structure and inline comments) | Robin: Pico remote, MQTT, ADC, ThingSpeak, AI, main application |
