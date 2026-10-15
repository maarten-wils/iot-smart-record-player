# Bouwplan Smart Record Player

Van nul tot het volledige project, stap voor stap.

| Deel | Wat | Requirement |
| --- | --- | --- |
| 1 | Maartens opstelling nabouwen | digitaal out, PWM, motor, I2C, SPI-OLED |
| 2 | Pico-afstandsbediening via MQTT | MQTT via Pico, ultrasoon, digitaal in |
| 3 | Volumeknop: potmeter + MCP3008 | SPI analog in |
| 4 | ThingSpeak online dashboard | dashboard online |
| 5 | AI-weetjes over de artiest | extra: AI |
| 6 | Alles samen + eigen platen | demo |

Werk steeds zo: **aansluiten → testen → pas dan verder.**
Werkt een stap niet, los het eerst op voor je meer bedrading toevoegt.
Alle pinnen staan ook samen in [pinout.md](pinout.md).

---

## 0. Klaarleggen

**Materiaal**
- [ ] Raspberry Pi 5 + voeding, microSD met Raspberry Pi OS
- [ ] Breadboard + dupont-kabels (M-M, M-F)
- [ ] 28BYJ-48 stepper met ULN2003-driverbordje
- [ ] BH1750 lichtsensor
- [ ] OLED 128x64 (SPI)
- [ ] Rode LED + weerstand van 220 Ω
- [ ] Bluetooth-speaker
- [ ] MCP3008-chip + potmeter 10k
- [ ] Raspberry Pi Pico 2 WH + USB-kabel (met data)
- [ ] HC-SR04 ultrasone sensor
- [ ] Drukknop (voor de Pico)
- [ ] 3x weerstand van 1 kΩ (spanningsdeler)
- [ ] Optioneel: powerbank voor de Pico (dan is de afstandsbediening echt draadloos)

**Altijd:** Pi uitzetten en Pico loskoppelen voor je bedrading verandert.

---

## Deel 1: huidige opstelling nabouwen

### 1.1 Repo op de Pi

De repo is privé, dus `git clone` vraagt om in te loggen. Kies één van beide:

- Op GitHub: **Code → Download ZIP** en uitpakken in je home-map, of
- `gh auth login` en dan `gh repo clone maarten-wils/iot-smart-record-player`

Map `audio/`: zet daar minstens één muziekbestand in (`.ogg`, `.wav` of `.mp3`).
Het eerste nummer in `records.json` verwijst naar `audio/avalon-1920.ogg`: vraag dat aan
Maarten of zet een eigen bestand en pas de naam aan in `records.json` (zie deel 6).

- [ ] Repo staat op de Pi (`~/iot-smart-record-player`)
- [ ] Minstens één audiobestand in `audio/`

### 1.2 Interfaces aanzetten

```bash
sudo nano /boot/firmware/config.txt
```

Zorg dat deze regels erin staan:

```
dtparam=i2c_arm=on
dtparam=spi=on
dtoverlay=spi1-1cs
```

`spi=on` is voor de MCP3008 (deel 3), `spi1-1cs` voor de OLED.
Als de PWM-LED straks niet werkt, voeg dan ook toe: `dtoverlay=pwm,pin=12,func=4`

Opslaan (Ctrl+O, Enter, Ctrl+X) en `sudo reboot`.

- [ ] I2C, SPI0 en SPI1 aan

### 1.3 Python-omgeving en instellingen

```bash
cd ~/iot-smart-record-player
python3 -m venv ~/env
source ~/env/bin/activate
pip install -r requirements.txt
sudo apt install -y i2c-tools mosquitto mosquitto-clients
cp .env.example .env
nano .env
```

Zet in `.env` voorlopig `USE_VOLUME_KNOB=0` (de knob komt pas in deel 3).

Vanaf hier, **in elke nieuwe terminal**:
```bash
cd ~/iot-smart-record-player
source ~/env/bin/activate
```
Start scripts **zonder `sudo`**: `pw-play` werkt alleen in je eigen gebruikerssessie.

- [ ] venv werkt, `.env` aangemaakt

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

```bash
i2cdetect -y 1
```
✅ Je ziet `23` in de tabel.

```bash
python3 tests/test_lightsensor.py
```
✅ Lux-waarden lopen binnen. Dek de sensor af met je vinger: de waarde daalt.

**Noteer:** afgedekt = ____ lux, vrij = ____ lux.
De drempel `LIGHT_THRESHOLD` in `player/config.py` (nu 4) moet daartussen liggen.

- [ ] BH1750 OK

### 1.6 PWM-LED

| LED | Pi | Fysieke pin |
| --- | --- | ---: |
| lange poot (+), via 220 Ω | GPIO12 | 32 |
| korte poot (−) | GND | 34 |

Gebruik je een LED-module met ingebouwde weerstand, dan mag de 220 Ω weg.

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

```bash
python3 tests/test_pause_audio.py
```
✅ Muziek speelt; Enter pauzeert en hervat op dezelfde plek.
Hapert het hervatten, zet dan `PAUSE_MODE=restart` in `.env`.

- [ ] Audio OK, pauze OK

### 1.9 Maartens geïntegreerde test

```bash
python3 tests/test_tonearm_stepper.py
```

| Actie | Verwacht |
| --- | --- |
| Sensor afgedekt | REST: motor stil, LED zwak, OLED `REST`, geen geluid |
| Vinger weg | PLAY: motor draait, LED fel, OLED `PLAY`, muziek speelt |
| Ctrl+C | alles uit, scherm leeg |

- [ ] **Deel 1 klaar**

---

## Deel 2: Pico-afstandsbediening via MQTT

De Pico meet afstand met de HC-SR04 en leest een knop. Hij stuurt commando's via wifi
naar de MQTT-broker op de Pi. De Pi stuurt zijn status terug.

| Op de afstandsbediening | Gevolg |
| --- | --- |
| hand < 10 cm, 1 seconde | pauze / verder spelen |
| knop kort | volgende plaat |
| knop lang (1,5 s) | standby aan / uit |
| LED op de Pico | aan = PLAY, knippert = PAUSED, uit = REST / STANDBY |

### 2.1 Broker op de Pi

Mosquitto is al geïnstalleerd in 1.3. Laat de Pico toe vanaf het netwerk:

```bash
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

IP-adres van de Pi: `hostname -I` → ______________

- [ ] Broker OK

### 2.2 CircuitPython op de Pico

1. Download CircuitPython voor de **Raspberry Pi Pico 2 W** op circuitpython.org
   (niet de versie voor de gewone Pico W).
2. Hou de **BOOTSEL**-knop ingedrukt terwijl je de USB-kabel insteekt.
   De Pico verschijnt als schijf `RP2350`.
3. Sleep het `.uf2`-bestand erop. De Pico herstart als schijf `CIRCUITPY`.
4. Download de **Adafruit CircuitPython Library Bundle** (zelfde hoofdversie als je CircuitPython)
   en kopieer naar `CIRCUITPY/lib/`:
   - `adafruit_minimqtt/` (map)
   - `adafruit_connection_manager.mpy`
   - `adafruit_hcsr04.mpy`
   - `adafruit_ticks.mpy`
5. Open Thonny, kies rechtsonder de CircuitPython-interpreter, zodat je de console ziet.

- [ ] CircuitPython draait, libraries staan in `lib/`

### 2.3 Pico op het breadboard

Zet de Pi-onderdelen aan de ene kant (bv. rijen 1–35) en de Pico over de middengleuf
aan de andere kant (bv. rijen 40–63). **Gebruik voor de Pico de stroomrails niet**:
steek alle draden rechtstreeks in de rijen van de Pico-pinnen.

Pinnummers op de Pico: USB-poort bovenaan, pin 1 linksboven, links 1→20 naar beneden,
rechts 21→40 van onder naar boven. Pin 40 zit dus rechtsboven, naast de USB.

### 2.4 Test 1: HC-SR04

| HC-SR04 | Pico | Fysieke pin |
| --- | --- | ---: |
| VCC | VBUS (5 V) | 40 |
| GND | GND | 38 |
| TRIG | GP2 | 4 |
| ECHO | GP3, via spanningsdeler | 5 |

ECHO geeft 5 V terug, de Pico verdraagt maar 3,3 V:

```
ECHO ──[1 kΩ]──┬── GP3 (pin 5)
               │
            [1 kΩ]
               │
            [1 kΩ]
               │
              GND (pin 38)
```

Kopieer `pico/test_hcsr04.py` naar de Pico **als `code.py`**.
✅ Console: twee keer per seconde een afstand in cm; beweeg je hand en de waarde verandert.

- [ ] HC-SR04 OK

### 2.5 Test 2: knop

| Knop | Pico | Fysieke pin |
| --- | --- | ---: |
| poot 1 | GP15 | 20 |
| poot 2 | GND | 18 |

Geen weerstand nodig: de Pico gebruikt zijn interne pull-up.
Let op bij een knop met 4 pootjes: neem twee pootjes **diagonaal** tegenover elkaar.

Kopieer `pico/test_button.py` naar de Pico als `code.py`.
✅ `PRESSED` / `RELEASED` in de console, LED op de Pico brandt zolang je drukt.

- [ ] Knop OK

### 2.6 Test 3: wifi + MQTT

Kopieer `pico/settings.toml.example` naar `CIRCUITPY/settings.toml` en vul in:
wifi-naam, wachtwoord (2,4 GHz, geen gastnetwerk) en `MQTT_HOST` = IP van de Pi.
⚠️ `settings.toml` **nooit** in Git zetten.

Kopieer `pico/test_wifi_mqtt.py` naar de Pico als `code.py`. Op de Pi:
```bash
mosquitto_sub -h localhost -t 'recordplayer/#' -v
```
✅ Elke 2 seconden `recordplayer/remote/test hello 1`, `hello 2`, ...

- [ ] Wifi + MQTT OK

### 2.7 De echte afstandsbediening

Kopieer `pico/code.py` naar de Pico als `code.py`. Laat `mosquitto_sub` lopen.
- ✅ elke seconde `recordplayer/remote/distance ...`
- ✅ hand 1 s op ±5 cm → `recordplayer/remote/command TOGGLE` (één keer)
- ✅ knop kort → `NEXT`, knop lang → `POWER`

Stop `mosquitto_sub` en test de andere richting:
```bash
python3 tests/test_mqtt_pico.py
```
- typ `PLAY` → ✅ LED op de Pico aan
- typ `PAUSED` → ✅ LED knippert
- typ `REST` → ✅ LED uit

- [ ] **Deel 2 klaar: requirement "MQTT via Pico"**

### 2.8 Eerste volledige test

```bash
python3 record_player.py
```

| Actie | Verwacht |
| --- | --- |
| BH1750 vrij | PLAY: motor, LED fel, muziek, OLED `PLAY`, Pico-LED aan |
| Hand boven HC-SR04 (1 s) | PAUSED: motor en muziek stoppen, LED "ademt", Pico-LED knippert |
| Nog eens hand | PLAY: muziek gaat verder waar ze stopte |
| Knop lang | STANDBY: alles uit, OLED `STANDBY` |
| Knop lang | terug naar PLAY |
| BH1750 afdekken | REST |
| Ctrl+C | alles uit |

Neem een kort filmpje met je gsm: materiaal voor de eindvideo.

- [ ] Volledige app werkt met de Pico

---

## Deel 3: volumeknop (potmeter + MCP3008)

De Pi heeft geen analoge ingangen. De MCP3008 zet de spanning van de potmeter
(0 – 3,3 V) om naar een getal en stuurt dat via SPI0 naar de Pi.

### 3.1 Aansluiten

Zet de MCP3008 **over de middengleuf**, met het halve maantje (notch) naar boven.
Pin 1 zit links van het maantje, pinnen 1–8 links naar beneden, 9–16 rechts van onder naar boven.

```
          notch
   CH0  1 ┌─U─┐ 16  VDD   -> 3.3 V rail
   CH1  2 │   │ 15  VREF  -> 3.3 V rail
   CH2  3 │   │ 14  AGND  -> GND rail
   CH3  4 │   │ 13  CLK   -> Pi pin 23 (GPIO11)
   CH4  5 │   │ 12  DOUT  -> Pi pin 21 (GPIO9)
   CH5  6 │   │ 11  DIN   -> Pi pin 19 (GPIO10)
   CH6  7 │   │ 10  CS    -> Pi pin 22 (GPIO25)
   CH7  8 └───┘  9  DGND  -> GND rail
```

- 3,3 V-rail van het breadboard: van Pi pin 17 (de BH1750 mag daar ook op).
- GND-rail: van Pi pin 25.
- Potmeter: buitenste poot → 3,3 V-rail, middelste poot → CH0 (MCP-pin 1), andere buitenste poot → GND-rail.

⚠️ VDD en VREF op **3,3 V**, niet op 5 V: anders krijgt de Pi 5 V op MISO.

### 3.2 Testen

```bash
python3 tests/test_adc.py
```
✅ Draai aan de knop: `raw` gaat van ~0 tot ~65000, volume van 0 % tot 100 %.

```bash
python3 tests/test_volume_audio.py
```
✅ Muziek wordt luider en zachter als je draait.

Zet daarna in `.env`: `USE_VOLUME_KNOB=1`

- [ ] **Deel 3 klaar: requirement "SPI analog in"**

---

## Deel 4: ThingSpeak online dashboard

### 4.1 Kanaal aanmaken

1. Maak een gratis account op thingspeak.mathworks.com.
2. **Channels → New Channel**, naam "Smart Record Player". Vink 5 velden aan:
   | Veld | Naam |
   | --- | --- |
   | Field 1 | Play state (0 standby, 1 rest, 2 paused, 3 play) |
   | Field 2 | Light (lux) |
   | Field 3 | Volume (%) |
   | Field 4 | Remote distance (cm) |
   | Field 5 | Record number |
3. Save Channel. Noteer de **Channel ID**.
4. **Devices → MQTT → Add a new device**, kies je kanaal bij "Authorized channels",
   zet publish en subscribe aan. Download de credentials (Client ID, Username, Password).
5. Vul in `.env` in: `THINGSPEAK_CHANNEL_ID`, `THINGSPEAK_CLIENT_ID`, `THINGSPEAK_USERNAME`, `THINGSPEAK_PASSWORD`.

### 4.2 Testen

```bash
python3 tests/test_thingspeak.py
```
✅ Na ±35 s staan er drie nieuwe punten in de grafieken van je kanaal.

### 4.3 Dashboard mooi maken (voor de demo)

- **Add Widgets**: een *Gauge* voor volume (0–100), een *Numeric Display* voor lux,
  een *Lamp Indicator* voor field 1 (aan bij waarde 3 = PLAY).
- **Gespeelde platen**: elke nieuwe plaat stuurt een statusbericht "Now playing: ...".
  De lijst zie je op `https://api.thingspeak.com/channels/<CHANNEL_ID>/status.json`
  (bij een privékanaal met `?api_key=<READ_API_KEY>` erachter).
- Zet het kanaal op **Public** als je het tijdens de demo op een ander scherm wil tonen.

Het gratis plan aanvaardt max. 1 update per 15 s; het programma houdt daar rekening mee.

- [ ] **Deel 4 klaar: requirement "dashboard online"**

---

## Deel 5: AI-weetjes over de artiest

Bij elke nieuwe plaat vraagt de Pi aan een AI-model (Claude) één kort weetje over de artiest.
Dat verschijnt op de OLED, in `recordplayer/now_playing` en in de console.
Zonder sleutel of zonder internet gebruikt hij de reserve-weetjes uit `records.json`.

1. Maak een account op console.anthropic.com en zet er wat tegoed op
   (een weetje kost een fractie van een cent).
2. **API Keys → Create Key**, kopieer de sleutel.
3. Zet in `.env`: `ANTHROPIC_API_KEY=...`
   ⚠️ Deze sleutel nooit in Git of in een screenshot.

```bash
python3 tests/test_ai_fact.py
python3 tests/test_ai_fact.py "Queen" "Bohemian Rhapsody"
```
✅ `[ai] ...` met een weetje van max. ±100 tekens.
Zie je `[fallback]`, dan is er een probleem met de sleutel of het tegoed (de foutmelding staat erboven).

- [ ] **Deel 5 klaar: requirement "extra: AI"**

---

## Deel 6: alles samen

### 6.1 Eigen platen toevoegen

Zet audiobestanden in `audio/` en voeg ze toe aan `records.json`:

```json
[
  {"file": "audio/avalon-1920.ogg", "artist": "Al Jolson", "title": "Avalon (1920)", "facts": ["..."]},
  {"file": "audio/mijn-nummer.mp3", "artist": "Artiest", "title": "Titel", "facts": ["reserve-weetje"]}
]
```

Met een korte druk op de knop van de Pico wissel je van plaat.

### 6.2 Eindtest

```bash
python3 record_player.py
```

Laat in een tweede terminal `mosquitto_sub -h localhost -t 'recordplayer/#' -v` lopen
en open je ThingSpeak-kanaal.

| Actie | Verwacht | Requirement |
| --- | --- | --- |
| Start | OLED: REST, plaat 1, "Loading fun fact..." → AI-weetje | AI |
| BH1750 vrij | PLAY: motor, LED fel, muziek, Pico-LED aan | digitaal out, motor, PWM, I2C |
| Draai aan de potmeter | volume op OLED en luidspreker verandert | SPI analog in |
| Hand boven de Pico | PAUSED / PLAY | ultrasoon, MQTT via Pico |
| Knop kort | volgende plaat, nieuw weetje | digitaal in, AI |
| Knop lang | STANDBY / terug aan | digitaal in |
| ThingSpeak | grafieken bewegen, status "Now playing" | dashboard online |
| OLED | status, volume, artiest, titel, weetje | dashboard lokaal, SPI |

- [ ] **Alles werkt**

### 6.3 Demovideo (max. 5 min)

Volg de tabel van 6.2 van boven naar beneden en zeg bij elke stap welk requirement
je toont. Film ook kort het ThingSpeak-dashboard en de `mosquitto_sub`-terminal.

---

## Als iets niet werkt

| Probleem | Kijk naar |
| --- | --- |
| `i2cdetect` toont geen `23` | SDA/SCL omgewisseld? `dtparam=i2c_arm=on`? |
| OLED blijft zwart | `dtoverlay=spi1-1cs`? RES/DC goed? |
| PWM-LED doet niets | LED omgekeerd? `dtoverlay=pwm,pin=12,func=4` toevoegen |
| Geen geluid | speaker verbonden? `bluetoothctl connect ...`; script niet met `sudo` |
| Pauze hapert | `PAUSE_MODE=restart` in `.env` |
| `test_adc.py` geeft altijd 0 of 65535 | VDD/VREF/AGND/DGND aangesloten? DOUT en DIN omgewisseld? `dtparam=spi=on`? |
| Volume springt heen en weer | slecht contact potmeter; `VOLUME_DEADBAND` in `config.py` verhogen |
| `GPIO busy` / `pin in use` | een ander script loopt nog: Ctrl+C of `pkill -f record_player` |
| Pico: wifi-fout | SSID/wachtwoord in settings.toml, 2,4 GHz netwerk |
| Pico: geen verbinding met broker | IP van de Pi juist? `local.conf` aanwezig? zelfde netwerk? |
| Pico: geen afstanden | TRIG/ECHO omgewisseld? spanningsdeler? VCC op pin 40? |
| TOGGLE blijft herhalen | `RELEASE_DISTANCE` in `pico/code.py` verhogen |
| Knop reageert niet | twee pootjes diagonaal gebruiken |
| ThingSpeak: niets binnen | credentials in `.env`? device heeft toegang tot het kanaal? |
| AI: altijd `[fallback]` | sleutel juist? tegoed op het account? internet op de Pi? |
| `ModuleNotFoundError` op de Pi | venv niet actief: `source ~/env/bin/activate` |
| `ImportError` op de Pico | library ontbreekt in `CIRCUITPY/lib/` |

---

## Daarna

- Alles committen (zonder `.env` en `settings.toml`, die staan in `.gitignore`)
- Documenten afwerken: `docs/project-definition.md`, `docs/block-schematic.svg`, `docs/report-draft.md`
- Presentatie maken en video op YouTube zetten
