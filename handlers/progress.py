import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from keyboards.common import home_kb
from services.progress_service import get_stats

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(lambda c: c.data == "section:progress")
async def show_progress(callback: CallbackQuery) -> None:
    stats = await get_stats(callback.from_user.id)

    streak = stats["streak"]
    fire = "🔥" if streak >= 3 else "📅"
    days = "день" if streak == 1 else "дня" if 2 <= streak <= 4 else "дней"

    text = (
        f"📊 *Мой прогресс*\n\n"
        f"{fire} Серия: *{streak} {days}*\n"
        f"⭐ Очки: *{stats['points']}*\n"
        f"📘 Уроков пройдено: *{stats['lessons']}*\n"
        f"🧠 Слов изучено: *{stats['words']}*\n"
        f"🎯 Тестов пройдено: *{stats['tests']}*"
    )

    await callback.message.edit_text(text, reply_markup=home_kb(), parse_mode="Markdown")
    await callback.answer()
