"""Smart Record Player - main program on the Raspberry Pi.

Run from the repo root, without sudo:
    source ~/env/bin/activate
    python3 record_player.py

IoT Information-Value Loop:
    create       BH1750 (tonearm), potentiometer via MCP3008 (volume),
                 HC-SR04 + button on the Pico remote (gestures, next, power)
    communicate  MQTT: Pico <-> local broker <-> this program -> ThingSpeak
    analyze      state machine (player/state.py), AI artist facts
    act          stepper platter, PWM LED, audio, OLED, online dashboard

All settings are in player/config.py and .env.
"""

import time

from player import config, state
from player.ai_facts import FactProvider
from player.audio import AudioPlayer
from player.display import Display
from player.light_sensor import LightSensor
from player.mqtt_link import MqttLink
from player.records import load_records
from player.status_led import StatusLed
from player.stepper import Stepper
from player.thingspeak import ThingSpeak

LUX_INTERVAL = 0.25      # s between light sensor readings
VOLUME_INTERVAL = 0.1    # s between volume knob readings
PUBLISH_INTERVAL = 2.0   # s between lux/volume updates on the local broker
LOOP_DELAY = 0.02        # s main loop period


def main():
    records = load_records()
    player_state = state.PlayerState(len(records))

    # ---------- hardware ----------
    stepper = Stepper(config.STEPPER_PINS, config.STEPPER_DELAY, config.STEPPER_REVERSE)
    light_sensor = LightSensor(config.I2C_SCL, config.I2C_SDA, config.BH1750_ADDRESS)
    led = StatusLed(config.LED_PIN, config.LED_FREQUENCY, config.LED_DIM, config.LED_BRIGHT)
    display = Display(config.OLED_SPI, config.OLED_RESET, config.OLED_DC, config.OLED_CS)

    volume_knob = None
    if config.USE_VOLUME_KNOB:
        from player.volume_knob import VolumeKnob   # only needs the library when used
        volume_knob = VolumeKnob(config.ADC_SPI, config.ADC_CS, config.ADC_CHANNEL, config.VOLUME_DEADBAND)
        volume = volume_knob.percent
    else:
        volume = config.DEFAULT_VOLUME

    audio = AudioPlayer(config.PAUSE_MODE)
    audio.set_volume(volume)

    # ---------- network ----------
    mqtt_link = MqttLink()
    thingspeak = ThingSpeak()

    # ---------- AI facts ----------
    facts = {}            # record index -> fact text
    new_facts = []        # filled by the AI thread, emptied by the main loop

    def on_fact(index, fact, source):
        print(f"[ai] fact for record {index + 1} ({source}): {fact}")
        facts[index] = fact
        new_facts.append(index)

    fact_provider = FactProvider(on_fact)

    def select_record(index):
        facts[index] = "Loading fun fact..."
        fact_provider.request(index, records[index])

    select_record(player_state.record_index)

    # ---------- main loop ----------
    last_status = None
    last_lux_read = 0
    last_volume_read = 0
    last_publish = 0
    first_reading = True
    lux = 0.0
    pages_cache = {}

    print("Smart Record Player running. Ctrl+C to stop.")

    try:
        while True:
            now = time.monotonic()
            record_changed = False

            # 1. Tonearm position (BH1750 via I2C)
            if now - last_lux_read >= LUX_INTERVAL:
                reading = light_sensor.read_lux()
                if reading is not None:
                    lux = reading
                    if first_reading:
                        first_reading = False   # first value after startup is unreliable
                    else:
                        player_state.set_tonearm(lux >= config.LIGHT_THRESHOLD)
                last_lux_read = now

            # 2. Volume knob (potentiometer via MCP3008 / SPI0)
            if volume_knob and now - last_volume_read >= VOLUME_INTERVAL:
                volume, changed = volume_knob.read()
                if changed:
                    print(f"volume -> {volume}%")
                    audio.set_volume(volume)
                    mqtt_link.publish_value(config.TOPIC_VOLUME, volume)
                last_volume_read = now

            # 3. Commands from the Pico remote (MQTT)
            command = mqtt_link.next_command()
            while command:
                if player_state.handle_command(command):
                    record_changed = True
                    select_record(player_state.record_index)
                command = mqtt_link.next_command()

            # 4. React to a new state (or a new record while playing)
            status = player_state.status
            record = records[player_state.record_index]

            if status != last_status or (record_changed and status == state.PLAY):
                print(f"{lux:.1f} lux -> {status} ({record['artist']} - {record['title']})")

                if status == state.PLAY:
                    if last_status == state.PAUSED and not record_changed:
                        audio.resume()
                    else:
                        audio.play(record["path"])
                        thingspeak.log_now_playing(record["artist"], record["title"])
                    stepper.start()
                elif status == state.PAUSED:
                    audio.pause()
                    stepper.stop()
                else:   # REST or STANDBY
                    audio.stop()
                    stepper.stop()

                mqtt_link.publish_status(status)
                last_status = status

            # The song ended by itself: start it again (like a record on repeat).
            if status == state.PLAY and audio.finished():
                audio.play(record["path"])

            # 5. A new AI fact arrived: share it
            while new_facts:
                index = new_facts.pop(0)
                if index == player_state.record_index:
                    mqtt_link.publish_now_playing(records[index], facts[index])

            # 6. Local dashboard: PWM LED + OLED
            led.update(status)

            fact = facts.get(player_state.record_index, "")
            if fact not in pages_cache:
                pages_cache[fact] = display.fact_pages(fact)
            pages = pages_cache[fact]
            page = pages[int(now / config.FACT_PAGE_TIME) % len(pages)]
            display.show(status, volume, record["artist"], record["title"], page)

            # 7. Online: local broker values + ThingSpeak
            if now - last_publish >= PUBLISH_INTERVAL:
                mqtt_link.publish_value(config.TOPIC_LUX, f"{lux:.1f}")
                mqtt_link.publish_value(config.TOPIC_VOLUME, volume)
                last_publish = now

            thingspeak.update(
                status=status,
                lux=lux,
                volume=volume,
                distance=mqtt_link.distance,
                record=player_state.record_index + 1,
            )
            thingspeak.tick()

            time.sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        # Switch everything off, also after an error.
        for close in (audio.stop, stepper.close, led.close, display.close,
                      light_sensor.close, mqtt_link.close, thingspeak.close):
            try:
                close()
            except Exception as error:
                print(f"cleanup: {error}")
        if volume_knob:
            volume_knob.close()


if __name__ == "__main__":
    main()
