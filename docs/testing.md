# Testing

Activate the environment first:

```bash
source ~/env/bin/activate
```

## Standalone tests

```bash
python3 tests/test_stepper.py
python3 tests/test_button.py
python3 tests/test_lightsensor.py
python3 tests/test_oled.py
python3 tests/test_audio.py
```

Status: **PASS**

## Integrated record-player test

```bash
python3 tests/test_tonearm_stepper.py
```

Status: **PASS**

- below 4 lux -> REST -> motor stopped -> PWM LED dim -> OLED `REST` -> audio stopped
- 4 lux or higher -> PLAY -> platter rotates in the correct direction -> PWM LED bright -> OLED `PLAY` -> Bluetooth audio starts
- Ctrl+C -> motor stopped -> LED off -> OLED cleared -> audio stopped

Course-based code:

- stepper: wave drive with digital outputs
- BH1750: I2C with `busio` and `writeto_then_readfrom`
- PWM LED: `pwmio.PWMOut`
- OLED: Adafruit SSD1306 + PIL over SPI

Project-specific logic:

- 4 lux REST/PLAY threshold
- LEGO tonearm behaviour
- local Bluetooth audio via `pw-play`
