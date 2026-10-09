# Setup

## Stepper motor prototype

The 28BYJ-48 stepper motor is connected to a ULN2003 driver board. The ULN2003 is connected to the Raspberry Pi through the GPIO expansion board / Pi Cobbler.

### Connections

| ULN2003 | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| IN1 | GPIO17 | 11 |
| IN2 | GPIO18 | 12 |
| IN3 | GPIO27 | 13 |
| IN4 | GPIO22 | 15 |
| VCC | 5V | 2 |
| GND | GND | 6 |

The 28BYJ-48 motor is connected to the 5-pin motor connector on the ULN2003 board.

## Notes

- Power off the Raspberry Pi before changing wiring.
- The standalone test uses `board` and `digitalio`, matching the GPIO style used in the IoT Essentials course.
- The step sequence uses wave drive with a 10 ms delay between steps.
