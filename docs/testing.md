# Testing

Activate the environment first:

```bash
source ~/env/bin/activate
```

## Stepper

```bash
python3 tests/test_stepper.py
```

Status: **PASS**  
Motor rotates the LEGO coaster and stops correctly.

## Pushbutton

```bash
python3 tests/test_button.py
```

Status: **PASS**  
Reports `PRESSED` and `RELEASED`. Kept for a later manual control function.

## BH1750

```bash
python3 tests/test_lightsensor.py
```

Status: **PASS**  
Sensor responds on I2C and returns changing lux values.

## Tonearm + stepper

```bash
python3 tests/test_tonearm_stepper.py
```

Current calibration:

- below 4 lux -> REST -> motor stopped
- 4 lux or higher -> PLAY -> motor rotates

The BH1750 reading and stepper control are based on the IoT Essentials course examples. The threshold is project-specific application logic.
