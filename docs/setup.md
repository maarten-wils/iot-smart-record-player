# Setup

## Stepper motor

28BYJ-48 with ULN2003:

| ULN2003 | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| IN1 | GPIO17 | 11 |
| IN2 | GPIO18 | 12 |
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
