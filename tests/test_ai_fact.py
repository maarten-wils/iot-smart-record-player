# Test the AI artist facts without other hardware.
# With ANTHROPIC_API_KEY in .env: asks the AI for a fact.
# Without a key: shows a fallback fact from records.json.
#
# Run from the repo root:  python3 tests/test_ai_fact.py
#                          python3 tests/test_ai_fact.py "Queen" "Bohemian Rhapsody"

import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from player.ai_facts import FactProvider
from player.records import load_records

if len(sys.argv) >= 3:
    record = {"artist": sys.argv[1], "title": sys.argv[2], "facts": []}
else:
    record = load_records()[0]

done = threading.Event()


def on_fact(index, fact, source):
    print(f"\n[{source}] {fact}\n({len(fact)} characters)")
    done.set()


provider = FactProvider(on_fact)
print(f"Asking a fact about {record['artist']} - {record['title']} ...")
provider.request(0, record)

if not done.wait(timeout=30):
    print("No answer within 30 s")
