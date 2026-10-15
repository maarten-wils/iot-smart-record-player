# Unit test of the player logic (player/state.py).
# Needs no hardware: runs on any computer with Python 3.
#
# Run from the repo root:  python3 tests/test_state.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from player.state import PlayerState, STANDBY, REST, PLAY, PAUSED


def check(name, actual, expected):
    result = "PASS" if actual == expected else "FAIL"
    print(f"{result}  {name}: {actual}")
    return actual == expected


results = []
s = PlayerState(record_count=3)

results.append(check("start in REST", s.status, REST))

s.handle_command("TOGGLE")
results.append(check("TOGGLE in REST is ignored", s.status, REST))

s.set_tonearm(True)
results.append(check("tonearm on record -> PLAY", s.status, PLAY))

s.handle_command("TOGGLE")
results.append(check("TOGGLE -> PAUSED", s.status, PAUSED))

s.handle_command("TOGGLE")
results.append(check("TOGGLE again -> PLAY", s.status, PLAY))

s.handle_command("TOGGLE")
s.set_tonearm(False)
s.set_tonearm(True)
results.append(check("lifting tonearm clears pause", s.status, PLAY))

changed = s.handle_command("NEXT")
results.append(check("NEXT selects record 2", (changed, s.record_index), (True, 1)))

s.handle_command("NEXT")
s.handle_command("NEXT")
results.append(check("NEXT wraps around to record 1", s.record_index, 0))

s.handle_command("POWER")
results.append(check("POWER -> STANDBY", s.status, STANDBY))

s.handle_command("NEXT")
s.handle_command("TOGGLE")
results.append(check("commands ignored in STANDBY", (s.status, s.record_index), (STANDBY, 0)))

s.handle_command("power")
results.append(check("POWER again -> PLAY (lowercase ok)", s.status, PLAY))

print()
print("ALL PASS" if all(results) else f"{results.count(False)} FAILED")
sys.exit(0 if all(results) else 1)
