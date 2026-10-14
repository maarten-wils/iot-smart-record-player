# Bouwplan Smart Record Player

Deel 1: Maartens opstelling nabouwen en testen.
Deel 2: de Pico als afstandsbediening via MQTT.

Werk steeds in deze volgorde: **aansluiten → testen → pas dan verder.**
Werkt een stap niet, los ze eerst op voor je meer bedrading toevoegt.

---

## 0. Klaarleggen

**Materiaal**
- [ ] Raspberry Pi 5 + voeding, microSD met Raspberry Pi OS
- [ ] Breadboard + dupont-kabels (M-M, M-F)
- [ ] 28BYJ-48 stepper met ULN2003-driverbordje
- [ ] BH1750 lichtsensor
- [ ] OLED 128x64 (SPI)
- [ ] Rode LED + weerstand van 220 Ω
- [ ] Drukknop (optioneel, enkel voor `test_button.py`)
- [ ] Bluetooth-speaker
- [ ] Raspberry Pi Pico 2 WH + USB-kabel (met data)
- [ ] HC-SR04 ultrasone sensor
- [ ] 3x weerstand van 1 kΩ (spanningsdeler)

**Even aan Maarten vragen**
- [ ] De regels uit zijn `/boot/firmware/config.txt` die hij heeft toegevoegd (I2C, SPI1, PWM)
- [ ] Welke Python-packages in zijn `~/env` zitten (`pip freeze`)
- [ ] Het audiobestand `audio/avalon-1920.ogg` (staat niet in de repo)

**Altijd:** Pi uitzetten voor je bedrading verandert.

---

## Deel 1: huidige opstelling nabouwen

### 1.1 Repo op de Pi

De repo is privé, dus `git clone` vraagt om in te loggen. Kies één van beide:

- Op GitHub: **Code → Download ZIP** en uitpakken op de Pi, of
- `gh auth login` en dan `gh repo clone maarten-wils/iot-smart-record-player`

Zet daarna de nieuwe Pico/MQTT-bestanden erbij (als ze nog niet in de repo staan), met dezelfde mappenstructuur:

```
iot-smart-record-player/
├── record_player.py          (nieuw)
├── audio/avalon-1920.ogg     (van Maarten of eigen bestand)
├── docs/pico-mqtt.md         (nieuw)
├── pico/code.py              (nieuw)
├── pico/settings.toml.example (nieuw)
└── tests/test_mqtt_pico.py   (nieuw) + de bestaande tests
```

- [ ] Repo staat op de Pi
- [ ] Audiobestand staat in `audio/`

### 1.2 Interfaces aanzetten

```bash
sudo nano /boot/firmware/config.txt
```

Zorg dat deze regels erin staan (vergelijk met die van Maarten):

```
dtparam=i2c_arm=on
dtoverlay=spi1-1cs
```

Als de PWM-LED straks niet werkt, voeg dan ook deze regel toe:
```
dtoverlay=pwm,pin=12,func=4
```

Opslaan en `sudo reboot`.

- [ ] I2C en SPI1 aan

### 1.3 Python-omgeving

```bash
python3 -m venv ~/env
source ~/env/bin/activate
pip install adafruit-blinka adafruit-circuitpython-ssd1306 pillow paho-mqtt
```

Vanaf hier: **elke nieuwe terminal eerst `source ~/env/bin/activate`**, ga naar de
hoofdmap van de repo (`cd ~/iot-smart-record-player`) en start scripts **zonder `sudo`**.
Het audiopad is relatief aan die map, en `pw-play` werkt alleen in je eigen gebruikerssessie.

Gereserveerd voor de OLED, niet voor iets anders gebruiken: GPIO5, GPIO18, GPIO19.

- [ ] venv werkt

### 1.4 Stepper motor

| ULN2003 | Pi GPIO | Fysieke pin |
| --- | --- | ---: |
| IN1 | GPIO17 | 11 |
| IN2 | GPIO26 | 37 |
| IN3 | GPIO27 | 13 |
| IN4 | GPIO22 | 15 |
| VCC | 5V | 2 |
| GND | GND | 6 |

```bash
python3 tests/test_stepper.py
```
✅ De motor draait een stukje en de LEDjes op het driverbordje knipperen.

- [ ] Stepper OK

### 1.5 Lichtsensor BH1750 (I2C)

| BH1750 | Pi | Fysieke pin |
| --- | --- | ---: |
| SDA | GPIO2 | 3 |
| SCL | GPIO3 | 5 |
| VCC | 3.3V | 17 |
| GND | GND | 14 |

Controleer eerst of de Pi de sensor ziet:
```bash
i2cdetect -y 1
```
✅ Je ziet `23` in de tabel.

```bash
python3 tests/test_lightsensor.py
```
✅ Lux-waarden lopen binnen. Dek de sensor af met je vinger: de waarde daalt.

**Noteer hier je waarden:** afgedekt = ____ lux, vrij = ____ lux.
De drempel (`LIGHT_THRESHOLD`, nu 4) moet daar ergens tussen liggen.

- [ ] BH1750 OK

### 1.6 PWM-LED

| LED | Pi | Fysieke pin |
| --- | --- | ---: |
| lange poot (+), via 220 Ω (weglaten bij een LED-module met ingebouwde weerstand) | GPIO12 | 32 |
| korte poot (−) | GND | 34 |

```bash
python3 tests/test_pwm_led.py
```
✅ De LED wisselt elke seconde tussen zwak en fel.

- [ ] PWM-LED OK

### 1.7 OLED (SPI1)

| OLED | Pi | Fysieke pin |
| --- | --- | ---: |
| GND | GND | 39 |
| VCC | 3.3V | 1 |
| SCL | GPIO21 | 40 |
| SDA | GPIO20 | 38 |
| RES | GPIO4 | 7 |
| DC | GPIO6 | 31 |

```bash
python3 tests/test_oled.py
```
✅ Drie lijnen tekst op het scherm.

- [ ] OLED OK

### 1.8 Bluetooth-speaker

```bash
bluetoothctl
power on
scan on
# wacht tot je speaker verschijnt, noteer het MAC-adres
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
exit
```

```bash
python3 tests/test_audio.py
```
✅ Je hoort een pieptoon; met Enter stopt die.

- [ ] Audio OK

### 1.9 Alles samen

```bash
python3 tests/test_tonearm_stepper.py
```

| Actie | Verwacht |
| --- | --- |
| Sensor afgedekt | REST: motor stil, LED zwak, OLED `REST`, geen geluid |
| Vinger weg | PLAY: motor draait, LED fel, OLED `PLAY`, muziek speelt |
| Ctrl+C | alles uit, scherm leeg |

Schakelt hij niet goed om? Pas `LIGHT_THRESHOLD` aan met je genoteerde waarden.

- [ ] **Deel 1 klaar: Maartens opstelling werkt bij jou**

---

## Deel 2: Pico-afstandsbediening via MQTT

Hoe het werkt: de Pico meet afstand met de HC-SR04. Hou je je hand 1 seconde
dichter dan 10 cm, dan stuurt hij `TOGGLE` naar de Pi en pauzeert of hervat
de platenspeler. De Pi stuurt zijn status terug; de LED op de Pico brandt bij PLAY.
Alle berichten lopen via de MQTT-broker (Mosquitto) op de Pi.

### 2.1 Broker op de Pi

```bash
sudo apt install mosquitto mosquitto-clients
sudo tee /etc/mosquitto/conf.d/local.conf <<'EOF'
listener 1883
allow_anonymous true
EOF
sudo systemctl restart mosquitto
```

Test met twee terminals:
```bash
# terminal 1
mosquitto_sub -h localhost -t 'test' -v
# terminal 2
mosquitto_pub -h localhost -t 'test' -m 'hallo'
```
✅ In terminal 1 verschijnt `test hallo`.

Noteer het IP-adres van de Pi: `hostname -I` → ______________

- [ ] Broker OK

### 2.2 CircuitPython op de Pico

1. Download CircuitPython voor de **Raspberry Pi Pico 2 W** op circuitpython.org
   (niet de versie voor de gewone Pico W).
2. Hou de **BOOTSEL**-knop ingedrukt terwijl je de USB-kabel insteekt.
   De Pico verschijnt als schijf `RP2350`.
3. Sleep het `.uf2`-bestand erop. De Pico herstart als schijf `CIRCUITPY`.
4. Download de **Adafruit CircuitPython Library Bundle** (zelfde versienummer als je CircuitPython)
   en kopieer naar `CIRCUITPY/lib/`:
   - `adafruit_minimqtt/` (map)
   - `adafruit_connection_manager.mpy`
   - `adafruit_hcsr04.mpy`
   - `adafruit_ticks.mpy`
5. Open Thonny (of Mu) en kies de CircuitPython-interpreter, zodat je de console ziet.

- [ ] CircuitPython draait, libraries staan in `lib/`

### 2.3 Wifi-instellingen

Kopieer `pico/settings.toml.example` naar `CIRCUITPY/settings.toml` en vul in:
- je wifi-naam en wachtwoord (geen gastnetwerk: de Pico en de Pi moeten elkaar zien)
- `MQTT_HOST` = het IP-adres van de Pi uit 2.1

⚠️ `settings.toml` met je wachtwoord **nooit** in Git zetten.

- [ ] settings.toml ingevuld

### 2.4 HC-SR04 aansluiten

**Pico losgekoppeld van USB tijdens het bedraden.**

**Eén breadboard?** Zet de Pi-onderdelen aan de ene kant (bv. rijen 1–35) en de Pico
over de middengleuf aan de andere kant (bv. rijen 40–63). **Gebruik voor de Pico de
stroomrails niet**: steek de draden van de HC-SR04 rechtstreeks in de rijen van de
Pico-pinnen. De Pico is niet met de Pi bedraad; ze praten enkel via wifi (MQTT).
Met male-female dupont-kabels hoeft de HC-SR04 zelf niet op het breadboard.

| HC-SR04 | Pico | Fysieke pin |
| --- | --- | ---: |
| VCC | VBUS (5 V) | 40 |
| GND | GND | 38 |
| TRIG | GP2 | 4 |
| ECHO | GP3, via spanningsdeler | 5 |

ECHO geeft 5 V terug; de Pico verdraagt maar 3,3 V. Spanningsdeler met 3x 1 kΩ:

```
ECHO ──[1 kΩ]──┬── GP3
               │
            [1 kΩ]
               │
            [1 kΩ]
               │
              GND
```

Pinnummers op de Pico tel je met de USB-poort bovenaan: pin 1 is linksboven, linkerkant loopt 1→20,
rechterkant 21→40 van onder naar boven. Pin 40 is dus rechtsboven, naast de USB.

- [ ] HC-SR04 aangesloten, deler gecontroleerd

### 2.5 Pico-code testen

1. Kopieer `pico/code.py` naar `CIRCUITPY/code.py`. De Pico start het meteen.
2. Kijk in de Thonny-console:
   ✅ `my IP addr: ...` en `Connected to MQTT broker ...`
3. Op de Pi:
   ```bash
   mosquitto_sub -h localhost -t 'recordplayer/#' -v
   ```
   ✅ Elke seconde `recordplayer/remote/distance 42.3` (of je eigen afstand).
   Beweeg je hand: de afstand verandert.
4. Hou je hand 1 seconde op ±5 cm:
   ✅ `recordplayer/remote/command TOGGLE` (één keer, niet herhaald).

- [ ] Pico publiceert afstand en TOGGLE

### 2.6 Twee richtingen testen

Stop `mosquitto_sub` en start:
```bash
python3 tests/test_mqtt_pico.py
```
- typ `PLAY` + Enter → ✅ LED op de Pico gaat aan
- typ `REST` + Enter → ✅ LED gaat uit
- hand boven de sensor → ✅ `TOGGLE` verschijnt in dit venster

- [ ] MQTT werkt in beide richtingen

### 2.7 Alles samen

```bash
python3 record_player.py
```

| Actie | Verwacht |
| --- | --- |
| BH1750 vrij | PLAY: motor, LED fel, muziek, OLED `PLAY`, Pico-LED aan |
| Hand boven HC-SR04 (1 s) | PAUSED: motor en muziek stoppen, OLED pauze-icoon, Pico-LED uit |
| Nog eens hand | PLAY: alles herneemt (muziek start opnieuw vanaf begin) |
| BH1750 afdekken | REST: alles stopt, pauze wordt gewist |
| Ctrl+C | alles uit |

- [ ] **Deel 2 klaar: requirement "MQTT via Pico" werkt**

Neem hier meteen een kort filmpje van met je gsm. Dat is materiaal voor de eindvideo.

---

## Als iets niet werkt

| Probleem | Kijk naar |
| --- | --- |
| `i2cdetect` toont geen `23` | SDA/SCL omgewisseld? I2C aan in config.txt? |
| OLED blijft zwart | `dtoverlay=spi1-1cs` aanwezig? RES/DC goed? |
| PWM-LED doet niets | LED omgekeerd? `dtoverlay=pwm,pin=12,func=4` toevoegen |
| Geen geluid | Speaker nog verbonden? `bluetoothctl connect ...` opnieuw |
| Pico: wifi-fout | SSID/wachtwoord in settings.toml, 2.4 GHz netwerk |
| Pico: geen verbinding met broker | IP van de Pi juist? `local.conf` aanwezig? Zelfde netwerk? |
| Geen afstanden | TRIG/ECHO omgewisseld? Spanningsdeler juist? VCC op pin 40? |
| TOGGLE blijft herhalen | `RELEASE_DISTANCE` in `code.py` verhogen |
| `ModuleNotFoundError` op de Pi | venv niet actief: `source ~/env/bin/activate` |
| `ImportError` op de Pico | library ontbreekt in `CIRCUITPY/lib/` |

---

## Daarna

1. Bestanden committen naar de repo (zonder `settings.toml`)
2. ADC: MCP3008 + potmeter als volumeknop
3. ThingSpeak: grafieken voor lux, status, volume
4. AI: weetje over de band bij het starten van een plaat
5. Documenten: projectdefinitie, blokschema, rapport, presentatie, video
