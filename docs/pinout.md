# Pinout

All connections in one place. Physical pin numbers: Raspberry Pi 40-pin header,
pin 1 = 3.3V next to the SD-card side; Pico pin 1 = top left with the USB port up.

## Raspberry Pi 5

| Pin | GPIO | Connected to | Part |
| ---: | --- | --- | --- |
| 1 | 3.3V | VCC | OLED |
| 2 | 5V | VCC | ULN2003 (stepper) |
| 3 | GPIO2 / SDA1 | SDA | BH1750 |
| 5 | GPIO3 / SCL1 | SCL | BH1750 |
| 6 | GND | GND | ULN2003 |
| 7 | GPIO4 | RES | OLED |
| 11 | GPIO17 | IN1 | ULN2003 |
| 13 | GPIO27 | IN3 | ULN2003 |
| 14 | GND | GND | BH1750 |
| 15 | GPIO22 | IN4 | ULN2003 |
| 16 | GPIO23 | pushbutton (Maarten's `test_button.py`, optional) | button |
| 17 | 3.3V | 3.3 V rail: BH1750 VCC, MCP3008 VDD + VREF, potentiometer | rail |
| 19 | GPIO10 / SPI0 MOSI | DIN (pin 11) | MCP3008 |
| 21 | GPIO9 / SPI0 MISO | DOUT (pin 12) | MCP3008 |
| 22 | GPIO25 | CS (pin 10) | MCP3008 |
| 23 | GPIO11 / SPI0 SCLK | CLK (pin 13) | MCP3008 |
| 25 | GND | GND rail: MCP3008 AGND + DGND, potentiometer | rail |
| 31 | GPIO6 | DC | OLED |
| 32 | GPIO12 / PWM0 | LED + (via 220 Ω) | status LED |
| 34 | GND | LED − | status LED |
| 37 | GPIO26 | IN2 | ULN2003 |
| 38 | GPIO20 / SPI1 MOSI | SDA | OLED |
| 39 | GND | GND | OLED |
| 40 | GPIO21 / SPI1 SCLK | SCL | OLED |

Reserved, keep free: GPIO5 (software CS of the OLED), GPIO18 (SPI1 CE0), GPIO19 (SPI1 MISO),
GPIO7 and GPIO8 (SPI0 CE1/CE0, claimed by the kernel when SPI0 is on).

`/boot/firmware/config.txt`:

```
dtparam=i2c_arm=on
dtparam=spi=on
dtoverlay=spi1-1cs
```

## MCP3008 (DIP-16, notch at the top)

```
          notch
   CH0  1 ┌─U─┐ 16  VDD   -> 3.3 V
   CH1  2 │   │ 15  VREF  -> 3.3 V
   CH2  3 │   │ 14  AGND  -> GND
   CH3  4 │   │ 13  CLK   -> Pi pin 23 (GPIO11)
   CH4  5 │   │ 12  DOUT  -> Pi pin 21 (GPIO9)
   CH5  6 │   │ 11  DIN   -> Pi pin 19 (GPIO10)
   CH6  7 │   │ 10  CS    -> Pi pin 22 (GPIO25)
   CH7  8 └───┘  9  DGND  -> GND
```

Potentiometer (10k): outer leg -> 3.3 V, middle leg (wiper) -> CH0 (pin 1), other outer leg -> GND.

## Raspberry Pi Pico 2 W (remote)

| Pin | GPIO | Connected to | Part |
| ---: | --- | --- | --- |
| 4 | GP2 | TRIG | HC-SR04 |
| 5 | GP3 | ECHO via voltage divider | HC-SR04 |
| 18 | GND | pushbutton leg 2 | button |
| 20 | GP15 | pushbutton leg 1 (internal pull-up) | button |
| 38 | GND | GND + bottom of voltage divider | HC-SR04 |
| 40 | VBUS (5 V) | VCC | HC-SR04 |
| – | onboard LED | status: on = PLAY, blinking = PAUSED | LED |

Voltage divider (ECHO is 5 V, the Pico accepts 3.3 V):

```
ECHO ──[1 kΩ]──┬── GP3 (pin 5)
               │
            [1 kΩ]
               │
            [1 kΩ]
               │
              GND (pin 38)
```

The Pico is **not wired to the Raspberry Pi**: they only talk over WiFi (MQTT).
Do not connect the Pico to the breadboard power rails of the Pi.
