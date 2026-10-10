# Setup

## Stepper motor

The 28BYJ-48 stepper motor is connected to a ULN2003 driver board.

| ULN2003 | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| IN1 | GPIO17 | 11 |
| IN2 | GPIO18 | 12 |
| IN3 | GPIO27 | 13 |
| IN4 | GPIO22 | 15 |
| VCC | 5V | 2 |
| GND | GND | 6 |

The motor is connected to the 5-pin motor connector on the ULN2003 board.

The stepper test uses wave drive with a 10 ms delay between steps, following the IoT Essentials course approach.

## BH1750 light sensor

The BH1750 is connected through I2C1.

| BH1750 | Raspberry Pi | Physical pin |
| --- | --- | ---: |
| SDA | GPIO2 / SDA1 | 3 |
| SCL | GPIO3 / SCL1 | 5 |
| VCC | 3.3V | 17 |
| GND | GND | 14 |

The sensor is built into the LEGO record-player setup. The tonearm changes how much light reaches the sensor.

Current measured values after mechanical adjustment:

- REST: approximately 22-27 lux
- PLAY: approximately 2.5 lux
- threshold: 10 lux

## Pushbutton

The standalone pushbutton test is kept for later use. The previous direct button-to-stepper integration is no longer part of the current design.

## Notes

- Power off the Raspberry Pi before changing wiring.
- `board`, `digitalio` and `busio` are used in the same style as the IoT Essentials course examples.
- The BH1750 uses I2C address `0x23` and high-resolution command `0x10` as in the course example.
