# Testing

## Stepper motor standalone test

### Purpose

Verify that the 28BYJ-48 stepper motor and ULN2003 driver can start, rotate a lightweight coaster and stop reliably before integrating RFID, audio or other components.

### Test command

```bash
source ~/env/bin/activate
python3 tests/test_stepper.py
```

### Expected result

- The ULN2003 input LEDs switch in sequence.
- The stepper motor rotates.
- A lightweight coaster attached to the motor rotates with it.
- The motor stops when the test finishes.

### Verified result

Status: **PASS**

The standalone stepper test was repeated successfully. The motor starts and stops correctly and can rotate the lightweight coaster.

The current short test does not make the coaster complete a full revolution. This is acceptable for this milestone because the goal is to prove reliable physical rotation and stop/start behaviour. A longer rotation can be added later when the final playback behaviour is implemented.
