# Unit test of the record list (player/records.py) with the Record Library app.
# Needs no hardware: runs on any computer with Python 3.
#
# Run from the repo root:  python3 tests/test_records.py

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from player import config, records


def check(name, actual, expected):
    result = "PASS" if actual == expected else "FAIL"
    print(f"{result}  {name}: {actual}")
    return actual == expected


results = []
folder = Path(tempfile.mkdtemp())
(folder / "audio").mkdir()

config.RECORDS_FILE = folder / "records.json"
records.LIBRARY_FILE = folder / "audio" / "library.json"

config.RECORDS_FILE.write_text(json.dumps([
    {"file": "audio/a.mp3", "artist": "A", "title": "Song A", "rfid_uid": "d5293d0a"},
    {"file": "audio/b.mp3", "artist": "B", "title": "Song B", "rfid_uid": "c5e63f0a"},
]))


def titles():
    return [record["title"] for record in records.load_records()]


results.append(check("no library.json -> records.json only", titles(), ["Song A", "Song B"]))
results.append(check("no library.json -> no mtime", records.library_mtime(), None))

records.LIBRARY_FILE.write_text(json.dumps([
    {"rfid": "A1B2C3D4", "file": "audio/new.mp3", "artist": "N", "title": "New", "facts": []},
]))
loaded = records.load_records()
results.append(check("library record added", [r["title"] for r in loaded], ["Song A", "Song B", "New"]))
results.append(check("rfid becomes lowercase rfid_uid", loaded[2]["rfid_uid"], "a1b2c3d4"))
results.append(check("mtime exists", records.library_mtime() is not None, True))

records.LIBRARY_FILE.write_text(json.dumps([
    {"rfid": "c5e63f0a", "file": "audio/other.mp3", "artist": "X", "title": "Replaced B"},
]))
results.append(check("same tag replaces records.json record", titles(), ["Song A", "Replaced B"]))

records.LIBRARY_FILE.write_text("{ half written")
results.append(check("invalid library.json is ignored", titles(), ["Song A", "Song B"]))

records.LIBRARY_FILE.write_text(json.dumps([{"artist": "no tag, no file"}]))
results.append(check("incomplete library record is skipped", titles(), ["Song A", "Song B"]))

print()
print("ALL PASS" if all(results) else "SOME TESTS FAILED")
sys.exit(0 if all(results) else 1)
