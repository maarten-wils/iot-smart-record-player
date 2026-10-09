# IoT Smart Record Player

IoT Essentials team project prototype.

## Current milestone

Standalone stepper motor prototype using:

- Raspberry Pi 5
- 28BYJ-48 5V stepper motor
- ULN2003 driver board
- GPIO expansion board / Pi Cobbler

The current prototype has been tested successfully: the motor starts, rotates a lightweight coaster and stops correctly.

## Current GPIO mapping

| ULN2003 | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| IN1 | GPIO17 | 11 |
| IN2 | GPIO18 | 12 |
| IN3 | GPIO27 | 13 |
| IN4 | GPIO22 | 15 |
| VCC | 5V | 2 |
| GND | GND | 6 |

## Run the stepper test

Activate the existing Python environment and run:

```bash
source ~/env/bin/activate
python3 tests/test_stepper.py
```

See `docs/setup.md` and `docs/testing.md` for the current hardware setup and verified test result.
