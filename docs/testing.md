# Testing

## Stepper motor standalone test

Command:

```bash
python3 tests/test_stepper.py
```

Status: **PASS**

Verified behaviour:

- ULN2003 inputs switch in sequence
- stepper motor rotates
- LEGO coaster rotates
- motor stops after the test

## Pushbutton standalone test

Command:

```bash
python3 tests/test_button.py
```

Status: **PASS**

The pushbutton correctly reports RELEASED and PRESSED. It is kept for a later manual control function.

## BH1750 standalone test

Command:

```bash
python3 tests/test_lightsensor.py
```

Status: **PASS**

The BH1750 was detected on I2C address `0x23` and returns changing lux values.

## Tonearm detection test

Command:

```bash
python3 tests/test_tonearm.py
```

Status: **PASS**

After mechanical adjustment the measured values were clearly separated:

- REST: approximately 22-27 lux
- PLAY: approximately 2.5 lux

A threshold of 10 lux is used:

- below 10 lux -> PLAY
- 10 lux or higher -> REST

## Tonearm + stepper integration test

Command:

```bash
python3 tests/test_tonearm_stepper.py
```

Status: **PASS**

Verified behaviour:

- REST -> motor stopped
- PLAY -> motor rotates
- returning to REST -> motor stops

The integration combines the course-based BH1750 I2C reading with the course-based wave-drive stepper control. The threshold and PLAY/REST decision are project-specific application logic.
