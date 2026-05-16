import logging
from datetime import date, timedelta
from typing import Optional

import aiosqlite

from config import config
from database.models import User

logger = logging.getLogger(__name__)


async def get_or_create_user(user_id: int, username: Optional[str], first_name: str) -> User:
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()

        if not row:
            await db.execute(
                "INSERT INTO users (user_id, username, first_name, last_activity) VALUES (?, ?, ?, ?)",
                (user_id, username, first_name, today),
            )
            await db.commit()
            return User(user_id=user_id, username=username, first_name=first_name, last_activity=today)

        streak = row["streak"]
        last = row["last_activity"]

        if last == today:
            pass
        elif last == yesterday:
            streak += 1
            await db.execute(
                "UPDATE users SET streak=?, last_activity=?, username=?, first_name=? WHERE user_id=?",
                (streak, today, username, first_name, user_id),
            )
            await db.commit()
        else:
            streak = 1
            await db.execute(
                "UPDATE users SET streak=1, last_activity=?, username=?, first_name=? WHERE user_id=?",
                (today, username, first_name, user_id),
            )
            await db.commit()

        return User(
            user_id=row["user_id"],
            username=row["username"],
            first_name=row["first_name"],
            streak=streak,
            total_points=row["total_points"],
            last_activity=row["last_activity"],
        )


async def add_points(user_id: int, points: int) -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "UPDATE users SET total_points = total_points + ? WHERE user_id = ?",
            (points, user_id),
        )
        await db.commit()


async def get_stats(user_id: int) -> dict:
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(
            "SELECT streak, total_points FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            user = await cur.fetchone()

        async with db.execute(
            "SELECT COUNT(*) AS n FROM lesson_progress WHERE user_id = ? AND completed = 1", (user_id,)
        ) as cur:
            lessons = (await cur.fetchone())["n"]

        async with db.execute(
            "SELECT COUNT(*) AS n FROM word_stats WHERE user_id = ?", (user_id,)
        ) as cur:
            words = (await cur.fetchone())["n"]

        async with db.execute(
            "SELECT COUNT(*) AS n FROM test_results WHERE user_id = ?", (user_id,)
        ) as cur:
            tests = (await cur.fetchone())["n"]

    return {
        "streak": user["streak"] if user else 0,
        "points": user["total_points"] if user else 0,
        "lessons": lessons,
        "words": words,
        "tests": tests,
    }


async def save_test_result(user_id: int, test_type: str, score: int, total: int) -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT INTO test_results (user_id, test_type, score, total) VALUES (?, ?, ?, ?)",
            (user_id, test_type, score, total),
        )
        await db.commit()
