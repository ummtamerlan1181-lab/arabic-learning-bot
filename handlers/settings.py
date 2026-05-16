import logging

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.common import home_kb

router = Router()
logger = logging.getLogger(__name__)


def _settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ℹ️ О боте", callback_data="settings:about")],
            [InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")],
        ]
    )


@router.callback_query(lambda c: c.data == "section:settings")
async def settings_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "⚙️ *Настройки*",
        reply_markup=_settings_kb(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings:about")
async def settings_about(callback: CallbackQuery) -> None:
    text = (
        "🤖 *Arabic Learning Bot*\n\n"
        "Помощник по изучению арабского языка для русскоязычных пользователей.\n\n"
        "Стек: Python · aiogram 3 · OpenAI API · SQLite\n\n"
        "Разделы: уроки, слова, упражнения, чтение, тесты, AI-помощник.\n\n"
        "Все упражнения и тесты генерируются AI в реальном времени."
    )
    await callback.message.edit_text(text, reply_markup=home_kb(), parse_mode="Markdown")
    await callback.answer()
