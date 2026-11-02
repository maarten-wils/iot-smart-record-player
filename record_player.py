"""Smart Record Player - main program on the Raspberry Pi.

Run from the repo root, without sudo:
    source ~/env/bin/activate
    python3 record_player.py

IoT Information-Value Loop:
    create       Pico sensors: BH1750, MCP3008, HC-SR04, button, RFID
    communicate  MQTT: Pico <-> local broker <-> this program -> ThingSpeak
    analyze      state machine (player/state.py), AI artist facts
    act          audio on Pi; Pico receives status for LED/OLED outputs

All settings are in player/config.py and .env.
"""

import time

from player import config, state
from player.ai_facts import FactProvider
from player.audio import AudioPlayer
from player.mqtt_link import MqttLink
from player.records import library_mtime, load_records
from player.thingspeak import ThingSpeak

LOOP_DELAY = 0.02
LIBRARY_CHECK_INTERVAL = 2.0   # seconds between checks for a changed library.json


def main():
    records = load_records()
    player_state = state.PlayerState(len(records))

    # Hardware sensors and local display outputs have moved to the Pico.
    # The Pi now receives sensor values through MQTT and keeps audio,
    # state handling, ThingSpeak and AI.
    audio = AudioPlayer(config.PAUSE_MODE)

    # Start muted until the Pico sends the real potentiometer value.
    audio.set_volume(0)

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

    # ---------- Record Library app ----------
    # The app writes audio/library.json on this Pi. Reload the records when
    # that file changes, so a new tag works without restarting the player.
    last_library_mtime = library_mtime()
    last_library_check = time.monotonic()

    def reload_records():
        current = records[player_state.record_index]
        current_key = (current.get("rfid_uid"), current["path"])

        try:
            new_records = load_records()
        except (OSError, ValueError, SystemExit) as error:
            print(f"[records] reload failed, keeping old list: {error}")
            return

        # Replace the contents in place: select_record() uses this list.
        records[:] = new_records
        player_state.record_count = max(1, len(records))

        # Keep the current record selected when it still exists.
        player_state.record_index = next(
            (
                index
                for index, item in enumerate(records)
                if (item.get("rfid_uid"), item["path"]) == current_key
            ),
            min(player_state.record_index, len(records) - 1),
        )
        print(f"[records] library changed -> {len(records)} record(s)")

    # ---------- main loop ----------
    last_status = None
    last_volume = None
    first_lux = True
    volume_ready = False
    lux = 0.0
    volume = 0

    print("Smart Record Player running. Ctrl+C to stop.")

    try:
        while True:
            record_changed = False

            # 0. Records added or changed with the Record Library app.
            now = time.monotonic()
            if now - last_library_check >= LIBRARY_CHECK_INTERVAL:
                last_library_check = now
                mtime = library_mtime()
                if mtime != last_library_mtime:
                    last_library_mtime = mtime
                    reload_records()

            # 1. Sensor values from the Pico over MQTT.
            if mqtt_link.lux is not None:
                lux = mqtt_link.lux

                if first_lux:
                    first_lux = False
                else:
                    player_state.set_tonearm(
                        lux >= config.LIGHT_THRESHOLD
                    )

            if mqtt_link.volume is not None:
                volume = mqtt_link.volume
                volume_ready = True

                if volume != last_volume:
                    print(f"volume -> {volume}%")
                    audio.set_volume(volume)
                    last_volume = volume

            # 2. RFID record selection.
            rfid_uid = mqtt_link.next_rfid()
            while rfid_uid:
                matched_index = next(
                    (
                        index
                        for index, item in enumerate(records)
                        if item.get("rfid_uid", "").lower() == rfid_uid.lower()
                    ),
                    None,
                )

                if matched_index is None:
                    print(f"[rfid] unknown tag: {rfid_uid}")
                else:
                    player_state.record_index = matched_index
                    player_state.paused = False
                    record_changed = True
                    select_record(matched_index)

                    selected = records[matched_index]
                    print(
                        f"[rfid] selected record {matched_index + 1}: "
                        f"{selected['artist']} - {selected['title']}"
                    )

                rfid_uid = mqtt_link.next_rfid()

            # 3. Commands from the Pico remote.
            command = mqtt_link.next_command()
            while command:
                if player_state.handle_command(command):
                    record_changed = True
                    select_record(player_state.record_index)
                command = mqtt_link.next_command()

            # 3. React to a new state (or a new record while playing).
            status = player_state.status
            record = records[player_state.record_index]

            if status != last_status or (record_changed and status == state.PLAY):
                print(
                    f"{lux:.1f} lux -> {status} "
                    f"({record['artist']} - {record['title']})"
                )

                if status == state.PLAY:
                    if not volume_ready:
                        print("[audio] waiting for Pico volume")
                    elif last_status == state.PAUSED and not record_changed:
                        audio.resume()
                    else:
                        # Apply the latest knob volume to the active audio sink
                        # immediately before playback starts.
                        audio.set_volume(volume)
                        audio.play(record["path"])
                        thingspeak.log_now_playing(
                            record["artist"],
                            record["title"]
                        )
                elif status == state.PAUSED:
                    audio.pause()
                else:   # REST or STANDBY
                    audio.stop()

                # Pico uses this retained status for its outputs.
                mqtt_link.publish_status(status)
                last_status = status

            # Start playback once the first real volume value arrives while in PLAY.
            if status == state.PLAY and volume_ready and audio.process is None:
                audio.set_volume(volume)
                audio.play(record["path"])

            # The song ended by itself: start it again (like a record on repeat).
            if status == state.PLAY and audio.finished():
                audio.set_volume(volume)
                audio.play(record["path"])

            # 4. A new AI fact arrived: share it.
            while new_facts:
                index = new_facts.pop(0)

                if index == player_state.record_index:
                    mqtt_link.publish_now_playing(
                        records[index],
                        facts[index]
                    )

            # 5. Online dashboard.
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
        for close in (
            audio.stop,
            mqtt_link.close,
            thingspeak.close,
        ):
            try:
                close()
            except Exception as error:
                print(f"cleanup: {error}")


if __name__ == "__main__":
    main()
