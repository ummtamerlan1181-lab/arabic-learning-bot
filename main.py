import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database.db import init_db
from handlers import ai_helper, exercises, lessons, progress, reading, settings, start, tests, words
from middlewares.throttling import ThrottlingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main() -> None:
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    await init_db()
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.7))

    for router in (
        start.router,
        lessons.router,
        words.router,
        exercises.router,
        reading.router,
        tests.router,
        progress.router,
        settings.router,
        ai_helper.router,
    ):
        dp.include_router(router)

    logging.getLogger(__name__).info("Bot started")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
