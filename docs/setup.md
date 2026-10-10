# Setup

## Stepper motor

28BYJ-48 with ULN2003:

| ULN2003 | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| IN1 | GPIO17 | 11 |
| IN2 | GPIO26 | 37 |
| IN3 | GPIO27 | 13 |
| IN4 | GPIO22 | 15 |
| VCC | 5V | 2 |
| GND | GND | 6 |

The stepper uses wave drive with a 10 ms delay between steps, following the IoT Essentials course approach.

## BH1750

Connected through I2C1:

| BH1750 | Raspberry Pi | Physical pin |
| --- | --- | ---: |
| SDA | GPIO2 / SDA1 | 3 |
| SCL | GPIO3 / SCL1 | 5 |
| VCC | 3.3V | 17 |
| GND | GND | 14 |

The LEGO tonearm changes the amount of light reaching the sensor.

Current calibration:

- REST -> below 4 lux
- PLAY -> 4 lux or higher

The BH1750 uses I2C address `0x23` and command `0x10`, matching the course example.

## PWM status LED

| LED | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| Signal | GPIO12 / PWM0 | 32 |
| GND | GND | shared GND |

The LED is dim in REST and bright in PLAY using `pwmio.PWMOut`.

## OLED display

128x64 SSD1306 OLED using the secondary SPI1 bus:

| OLED | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| GND | GND | 39 |
| VCC | 3.3V | 1 |
| SCL | GPIO21 / SPI1 SCLK | 40 |
| SDA | GPIO20 / SPI1 MOSI | 38 |
| RES | GPIO4 | 7 |
| DC | GPIO6 | 31 |

The OLED has no external CS pin. SPI1 is enabled with `dtoverlay=spi1-1cs` in `/boot/firmware/config.txt`.

The display shows `REST` or `PLAY` based on the same BH1750 state used for the motor and PWM LED.
