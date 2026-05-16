import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import config
from database.db import init_db
from handlers import ai_helper, exercises, lessons, progress, reading, settings, start, tests, words
from middlewares.throttling import ThrottlingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "") + WEBHOOK_PATH
PORT = int(os.getenv("PORT", 8000))


async def on_startup(bot: Bot) -> None:
    await init_db()
    await bot.set_webhook(WEBHOOK_URL)
    logging.getLogger(__name__).info("Bot started via webhook: %s", WEBHOOK_URL)


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()


def build_app() -> web.Application:
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

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

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()

    async def healthcheck(request: web.Request) -> web.Response:
        return web.Response(text="OK")

    app.router.add_get("/", healthcheck)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    return app


if __name__ == "__main__":
    web.run_app(build_app(), host="0.0.0.0", port=PORT)
