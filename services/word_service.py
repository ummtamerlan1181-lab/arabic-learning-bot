import json
from datetime import date
from pathlib import Path
from typing import Optional

_WORDS: list = []


def _load() -> list:
    global _WORDS
    if not _WORDS:
        path = Path(__file__).parent.parent / "data" / "words.json"
        with open(path, encoding="utf-8") as f:
            _WORDS = json.load(f)
    return _WORDS


def get_all() -> list:
    return _load()


def get_by_theme(theme: str) -> list:
    return [w for w in get_all() if w["theme"] == theme]


def get_by_id(word_id: str) -> Optional[dict]:
    return next((w for w in get_all() if w["id"] == word_id), None)


def get_daily() -> dict:
    words = get_all()
    return words[date.today().toordinal() % len(words)]


def get_next(theme: str, current_id: str) -> Optional[dict]:
    themed = get_by_theme(theme)
    ids = [w["id"] for w in themed]
    if current_id not in ids:
        return themed[0] if themed else None
    i = ids.index(current_id)
    return themed[i + 1] if i + 1 < len(themed) else None
