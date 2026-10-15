"""Record list: which audio file belongs to which artist / title.

Edit records.json in the repo root to add your own records:
    {"file": "audio/song.ogg", "artist": "...", "title": "...", "facts": ["optional fallback fact"]}
"""

import json

from . import config


def load_records():
    with open(config.RECORDS_FILE, encoding="utf-8") as file:
        records = json.load(file)
    if not records:
        raise SystemExit("records.json is empty: add at least one record")
    # Relative paths in records.json are relative to the repo root.
    for record in records:
        record["path"] = str(config.BASE_DIR / record["file"])
    return records
