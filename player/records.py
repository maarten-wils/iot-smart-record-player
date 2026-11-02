"""Record list: which audio file belongs to which artist / title / RFID tag.

Two sources, combined:

1. records.json in the repo root (in git), the default records:
    {"file": "audio/song.ogg", "artist": "...", "title": "...",
     "rfid_uid": "a1b2c3d4"}

2. audio/library.json (optional, NOT in git because audio/ is ignored),
   written by the Record Library app (github.com/r-wils/record-library-app):
    {"rfid": "a1b2c3d4", "file": "audio/song.mp3", "artist": "...",
     "title": "..."}

Library records are added after the records.json records. When a library
record uses the same RFID tag as a record in records.json, the library
record replaces it. Without library.json the player works exactly as
before, with records.json only.
"""

import json

from . import config

LIBRARY_FILE = config.BASE_DIR / "audio" / "library.json"


def _normalize_uid(uid):
    return "".join(ch for ch in str(uid or "").strip().lower() if ch in "0123456789abcdef")


def library_mtime():
    """Last change time of library.json, or None when it does not exist."""
    try:
        return LIBRARY_FILE.stat().st_mtime
    except OSError:
        return None


def _load_library():
    """Records from library.json; an empty list when missing or invalid."""
    if not LIBRARY_FILE.exists():
        return []
    try:
        with open(LIBRARY_FILE, encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError) as error:
        print(f"[records] library.json ignored: {error}")
        return []
    if not isinstance(data, list):
        print("[records] library.json ignored: not a list")
        return []

    records = []
    for item in data:
        if not isinstance(item, dict):
            continue
        uid = _normalize_uid(item.get("rfid") or item.get("rfid_uid"))
        if not uid or not item.get("file"):
            continue
        records.append({
            "file": item["file"],
            "artist": item.get("artist") or "Unknown artist",
            "title": item.get("title") or "Unknown title",
            "rfid_uid": uid,
        })
    return records


def load_records():
    with open(config.RECORDS_FILE, encoding="utf-8") as file:
        records = json.load(file)

    library = _load_library()
    library_uids = {item["rfid_uid"] for item in library}
    records = [
        record for record in records
        if _normalize_uid(record.get("rfid_uid")) not in library_uids
    ] + library

    if not records:
        raise SystemExit("records.json is empty: add at least one record")
    # Relative paths are relative to the repo root.
    for record in records:
        record["path"] = str(config.BASE_DIR / record["file"])
    if library:
        print(f"[records] {len(library)} record(s) from library.json")
    return records
