# Current pinout

Final wiring for the Pico-based prototype. Pico physical pin 1 is top-left with USB at the top.

## Pico 2 W

| Physical pin | GPIO | Connected to |
| ---: | --- | --- |
| 1 | GP0 | BH1750 SDA |
| 2 | GP1 | BH1750 SCL |
| 4 | GP2 | HC-SR04 TRIG |
| 5 | GP3 | HC-SR04 ECHO |
| 9 | GP6 | ULN2003 IN1 |
| 10 | GP7 | ULN2003 IN2 |
| 11 | GP8 | ULN2003 IN3 |
| 12 | GP9 | ULN2003 IN4 |
| 14 | GP10 | OLED SCL / SPI1 clock |
| 15 | GP11 | OLED SDA / SPI1 MOSI |
| 16 | GP12 | PWM status LED |
| 17 | GP13 | OLED DC |
| 20 | GP15 | pushbutton, internal pull-up |
| 21 | GP16 | SPI0 MISO: MCP3008 DOUT + RC522 MISO |
| 22 | GP17 | MCP3008 CS |
| 24 | GP18 | SPI0 SCK: MCP3008 CLK + RC522 SCK |
| 25 | GP19 | SPI0 MOSI: MCP3008 DIN + RC522 MOSI |
| 26 | GP20 | RC522 SDA/SS (SPI CS) |
| 27 | GP21 | RC522 RST |
| 29 | GP22 | OLED RESET |
| 40 | VBUS 5V | ULN2003 VCC in prototype |

OLED has no physical CS pin. GP5 is used only as the software CS required by `FourWire`; no wire is connected to GP5.

## Power

- 3.3V: BH1750, HC-SR04, MCP3008, potentiometer, RC522, OLED
- 5V: ULN2003/stepper
- all modules share common GND
- final one-cable power distribution still needs to be validated after mounting in the prototype

## MCP3008 + 10k potentiometer

MCP3008 DIP-16, notch up:

| MCP3008 pin | Function | Connection |
| ---: | --- | --- |
| 1 | CH0 | potentiometer wiper |
| 16 | VDD | 3.3V |
| 15 | VREF | 3.3V |
| 14 | AGND | GND |
| 13 | CLK | GP18 |
| 12 | DOUT | GP16 |
| 11 | DIN | GP19 |
| 10 | CS | GP17 |
| 9 | DGND | GND |

Potentiometer: one outer leg -> 3.3V, middle -> CH0, other outer leg -> GND.

## HC-SR04

- VCC -> 3.3V
- GND -> common GND
- TRIG -> GP2
- ECHO -> GP3 directly
- no resistor divider is used in this prototype setup

## Raspberry Pi 5

No project sensors are currently connected directly to the Pi 5. The Pi runs Mosquitto, player logic, Bluetooth audio, ThingSpeak and AI/fallback facts. Pico and Pi communicate over WiFi/MQTT.
