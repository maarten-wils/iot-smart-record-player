"""Player state machine.

Pure logic without hardware, so it can be unit tested on any computer
(see tests/test_state.py).

States:
    STANDBY  power switched off with the remote's button (long press)
    REST     tonearm on its rest (dark BH1750)
    PLAY     tonearm on the record (light BH1750)
    PAUSED   tonearm on the record, paused with a hand gesture

Commands from the Pico remote (MQTT):
    TOGGLE   pause / resume (only while the tonearm is on the record)
    NEXT     select the next record
    POWER    standby on / off
"""

STANDBY = "STANDBY"
REST = "REST"
PLAY = "PLAY"
PAUSED = "PAUSED"


class PlayerState:
    def __init__(self, record_count):
        self.record_count = max(1, record_count)
        self.record_index = 0
        self.powered = True
        self.arm_play = False
        self.paused = False

    def set_tonearm(self, on_record):
        """Update the tonearm position from the light sensor."""
        self.arm_play = on_record
        if not on_record:
            # Lifting the tonearm clears a pause, like a real record player.
            self.paused = False

    def handle_command(self, command):
        """Apply a remote command. Returns True when another record was selected."""
        command = command.strip().upper()

        if command == "POWER":
            self.powered = not self.powered
            self.paused = False
            return False

        if not self.powered:
            return False  # ignore everything else in standby

        if command == "TOGGLE" and self.arm_play:
            self.paused = not self.paused
        elif command == "NEXT":
            self.record_index = (self.record_index + 1) % self.record_count
            self.paused = False
            return True

        return False

    @property
    def status(self):
        if not self.powered:
            return STANDBY
        if not self.arm_play:
            return REST
        if self.paused:
            return PAUSED
        return PLAY
