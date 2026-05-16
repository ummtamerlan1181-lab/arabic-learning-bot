import aiosqlite
from config import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY,
    username      TEXT,
    first_name    TEXT NOT NULL,
    streak        INTEGER DEFAULT 0,
    total_points  INTEGER DEFAULT 0,
    last_activity TEXT,
    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lesson_progress (
    user_id      INTEGER NOT NULL,
    lesson_id    TEXT NOT NULL,
    completed    INTEGER DEFAULT 0,
    score        INTEGER DEFAULT 0,
    completed_at TEXT,
    PRIMARY KEY (user_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS word_stats (
    user_id   INTEGER NOT NULL,
    word_id   TEXT NOT NULL,
    correct   INTEGER DEFAULT 0,
    incorrect INTEGER DEFAULT 0,
    last_seen TEXT,
    PRIMARY KEY (user_id, word_id)
);

CREATE TABLE IF NOT EXISTS test_results (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    test_type    TEXT NOT NULL,
    score        INTEGER NOT NULL,
    total        INTEGER NOT NULL,
    completed_at TEXT DEFAULT (datetime('now'))
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.commit()
