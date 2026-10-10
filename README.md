# IoT Smart Record Player

IoT Essentials team project prototype.

## Current prototype

- Raspberry Pi 5
- 28BYJ-48 stepper motor with ULN2003
- BH1750 light sensor via I2C
- LEGO tonearm and record-player setup
- pushbutton kept for a later manual control function

Current behaviour:

- tonearm in REST -> low light -> motor stopped
- tonearm in PLAY -> more light -> motor rotates
- current light threshold: 4 lux

## Connections

### Stepper motor / ULN2003

| ULN2003 | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| IN1 | GPIO17 | 11 |
| IN2 | GPIO18 | 12 |
| IN3 | GPIO27 | 13 |
| IN4 | GPIO22 | 15 |
| VCC | 5V | 2 |
| GND | GND | 6 |

### BH1750

| BH1750 | Raspberry Pi | Physical pin |
| --- | --- | ---: |
| SDA | GPIO2 / SDA1 | 3 |
| SCL | GPIO3 / SCL1 | 5 |
| VCC | 3.3V | 17 |
| GND | GND | 14 |

## Tests

```bash
source ~/env/bin/activate
python3 tests/test_stepper.py
python3 tests/test_button.py
python3 tests/test_lightsensor.py
python3 tests/test_tonearm_stepper.py
```

See `docs/setup.md` and `docs/testing.md` for the current setup and test status.
