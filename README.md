# IoT Smart Record Player

IoT Essentials team project prototype.

## Current prototype

- Raspberry Pi 5
- 28BYJ-48 stepper motor with ULN2003
- BH1750 light sensor via I2C
- built-in PWM status LED on GPIO12
- 128x64 SSD1306 OLED via SPI1
- Bluetooth speaker with local audio playback via `pw-play`
- LEGO tonearm and enclosed record-player setup
- pushbutton kept for a later manual control function

Current behaviour:

- tonearm in REST -> low light -> motor stopped -> LED dim -> OLED shows `REST` -> audio stopped
- tonearm in PLAY -> more light -> motor rotates -> LED bright -> OLED shows `PLAY` -> audio starts
- current light threshold: 4 lux
- platter direction corrected for normal record rotation

## Connections

### Stepper motor / ULN2003

| ULN2003 | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| IN1 | GPIO17 | 11 |
| IN2 | GPIO26 | 37 |
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

### PWM status LED

| LED | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| Signal | GPIO12 / PWM0 | 32 |
| GND | GND | shared GND |

### OLED display

| OLED | Raspberry Pi GPIO | Physical pin |
| --- | --- | ---: |
| GND | GND | 39 |
| VCC | 3.3V | 1 |
| SCL | GPIO21 / SPI1 SCLK | 40 |
| SDA | GPIO20 / SPI1 MOSI | 38 |
| RES | GPIO4 | 7 |
| DC | GPIO6 | 31 |

## Tests

```bash
source ~/env/bin/activate
python3 tests/test_stepper.py
python3 tests/test_button.py
python3 tests/test_lightsensor.py
python3 tests/test_oled.py
python3 tests/test_audio.py
python3 tests/test_tonearm_stepper.py
```

See `docs/setup.md` and `docs/testing.md` for the current setup and test status.
