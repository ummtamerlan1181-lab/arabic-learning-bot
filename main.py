import logging
import os
import sys
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

log.info("=== Bot starting ===")
log.info("Python: %s", sys.version)
log.info("BOT_TOKEN set: %s", bool(os.getenv("BOT_TOKEN")))
log.info("OPENAI_API_KEY set: %s", bool(os.getenv("OPENAI_API_KEY")))
log.info("WEBHOOK_URL: %s", os.getenv("WEBHOOK_URL", "(not set)"))
log.info("PORT: %s", os.getenv("PORT", "8000"))

try:
    from aiohttp import web
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    from config import config
    from database.db import init_db
    from handlers import ai_helper, exercises, lessons, progress, reading, settings, start, tests, words
    from middlewares.throttling import ThrottlingMiddleware

    log.info("All imports successful")
except Exception:
    log.critical("Import failed:\n%s", traceback.format_exc())
    sys.exit(1)

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").rstrip("/") + WEBHOOK_PATH
PORT = int(os.getenv("PORT", 8000))

log.info("Webhook URL: %s", WEBHOOK_URL)
log.info("Listening on port: %d", PORT)


async def on_startup(bot: Bot) -> None:
    try:
        await init_db()
        log.info("Database initialized")
        await bot.set_webhook(WEBHOOK_URL)
        log.info("Webhook set: %s", WEBHOOK_URL)
    except Exception:
        log.critical("on_startup failed:\n%s", traceback.format_exc())
        raise


async def on_shutdown(bot: Bot) -> None:
    try:
        await bot.delete_webhook()
        log.info("Webhook deleted")
    except Exception:
        log.warning("on_shutdown error: %s", traceback.format_exc())


def build_app() -> web.Application:
    try:
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
        app.router.add_get("/healthz", healthcheck)

        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        log.info("App built successfully")
        return app
    except Exception:
        log.critical("build_app failed:\n%s", traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    try:
        web.run_app(build_app(), host="0.0.0.0", port=PORT)
    except Exception:
        log.critical("run_app failed:\n%s", traceback.format_exc())
        sys.exit(1)
