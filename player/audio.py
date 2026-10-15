"""Audio playback on the Bluetooth speaker via PipeWire.

- play:   starts `pw-play <file>`
- pause:  freezes the pw-play process (SIGSTOP), so the song really pauses
- resume: continues it (SIGCONT)
- volume: system volume via `wpctl`, so it changes while a song plays

If pausing with signals gives glitches on your speaker, set
PAUSE_MODE=restart in .env: pause then stops the song and resume
starts it again from the beginning.
"""

import os
import signal
import subprocess


class AudioPlayer:
    def __init__(self, pause_mode="signal"):
        self.pause_mode = pause_mode
        self.process = None
        self.current_file = None
        self.paused = False

    def play(self, path):
        """Start a file from the beginning (stops what was playing)."""
        self.stop()
        if not os.path.exists(path):
            print(f"[audio] file not found: {path}")
            return False
        self.current_file = path
        self.process = subprocess.Popen(["pw-play", str(path)])
        self.paused = False
        return True

    def pause(self):
        if not self.process or self.paused:
            return
        if self.pause_mode == "signal":
            self.process.send_signal(signal.SIGSTOP)
        else:
            self._kill()
        self.paused = True

    def resume(self):
        if not self.paused:
            return
        if self.pause_mode == "signal" and self.process:
            self.process.send_signal(signal.SIGCONT)
            self.paused = False
        elif self.current_file:
            self.play(self.current_file)

    def stop(self):
        self._kill()
        self.paused = False

    def _kill(self):
        if self.process is None:
            return
        if self.paused and self.pause_mode == "signal":
            self.process.send_signal(signal.SIGCONT)   # a stopped process ignores terminate
        self.process.terminate()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.kill()
        self.process = None

    def finished(self):
        """True when the song ended by itself (not paused, not stopped)."""
        return self.process is not None and not self.paused and self.process.poll() is not None

    @staticmethod
    def set_volume(percent):
        """Set the PipeWire output volume (0 - 100 %)."""
        try:
            subprocess.Popen(
                ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{percent / 100:.2f}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            print("[audio] wpctl not found, volume not changed")
