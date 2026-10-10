# IoT Smart Record Player

IoT Essentials team project prototype.

## Current prototype

The current prototype uses:

- Raspberry Pi 5
- 28BYJ-48 5V stepper motor
- ULN2003 driver board
- BH1750 I2C light sensor
- LEGO record-player prototype

The stepper rotates the coaster. The BH1750 is built into the LEGO setup and detects the tonearm position by measuring the amount of light reaching the sensor.

Current tested behaviour:

- tonearm in REST: higher light value, motor stopped
- tonearm in PLAY: lower light value, motor rotates
- current threshold: 10 lux

The pushbutton standalone test is kept for a later manual control function.

## GPIO mapping

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

Activate the existing Python environment:

```bash
source ~/env/bin/activate
```

Useful tests:

```bash
python3 tests/test_stepper.py
python3 tests/test_button.py
python3 tests/test_lightsensor.py
python3 tests/test_tonearm.py
python3 tests/test_tonearm_stepper.py
```

See `docs/setup.md` and `docs/testing.md` for the current hardware setup and verified test results.
