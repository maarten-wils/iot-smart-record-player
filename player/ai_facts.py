"""AI artist facts.

When a record is selected, an AI model (Claude, via the Anthropic API) is
asked for one short fun fact about the artist. The request runs in a
background thread so the player never waits for the internet.

Without an API key, or when the request fails, a fact from records.json
is used instead, so the demo always works.
"""

import json
import random
import threading
import urllib.request

from . import config

PROMPT = (
    'Give one surprising, true fun fact about the music artist "{artist}" '
    '(the record playing is "{title}"). Maximum 100 characters, one sentence, '
    "no introduction, plain text. If you are not sure about a fact, give a "
    "general fact about the music style instead."
)


class FactProvider:
    def __init__(self, on_fact):
        """on_fact(record_index, fact, source) is called when a fact is ready."""
        self.on_fact = on_fact
        self.enabled = bool(config.AI_API_KEY)
        if not self.enabled:
            print("[ai] no ANTHROPIC_API_KEY in .env -> using facts from records.json")

    def request(self, record_index, record):
        thread = threading.Thread(target=self._work, args=(record_index, record), daemon=True)
        thread.start()

    def _work(self, record_index, record):
        fact, source = None, "fallback"
        if self.enabled:
            try:
                fact = self.ask_ai(record["artist"], record["title"])
                source = "ai"
            except Exception as error:   # network, quota, ... -> fall back
                print(f"[ai] request failed: {error}")
        if not fact:
            fact = self.fallback(record)
        self.on_fact(record_index, fact, source)

    @staticmethod
    def ask_ai(artist, title):
        body = {
            "model": config.AI_MODEL,
            "max_tokens": 120,
            "messages": [{"role": "user", "content": PROMPT.format(artist=artist, title=title)}],
        }
        request = urllib.request.Request(
            config.AI_API_URL,
            data=json.dumps(body).encode(),
            headers={
                "x-api-key": config.AI_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=config.AI_TIMEOUT) as response:
            data = json.loads(response.read())

        text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        return " ".join(text.split())[:160]   # one line, safety limit for the OLED

    @staticmethod
    def fallback(record):
        facts = record.get("facts") or []
        if facts:
            return random.choice(facts)
        return f"Now spinning {record['title']} by {record['artist']}."
