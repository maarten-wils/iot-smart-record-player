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

## OLED

```bash
python3 tests/test_oled.py
```

Status: **PASS**  
The SSD1306 OLED works on SPI1 and displays the standalone test text.

## Tonearm + stepper + PWM + OLED

```bash
python3 tests/test_tonearm_stepper.py
```

Status: **PASS**

Current calibration:

- below 4 lux -> REST -> motor stopped -> PWM LED dim -> OLED shows `REST`
- 4 lux or higher -> PLAY -> motor rotates -> PWM LED bright -> OLED shows `PLAY`
- Ctrl+C -> motor stopped -> PWM LED off -> OLED cleared

The BH1750 reading, stepper control, PWM output and OLED code are based on the IoT Essentials course examples. The threshold and REST/PLAY behaviour are project-specific application logic.
