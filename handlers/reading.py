import json
import logging
from pathlib import Path

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.common import back_home_kb

router = Router()
logger = logging.getLogger(__name__)

_TEXTS: list = []


def _load() -> list:
    global _TEXTS
    if not _TEXTS:
        path = Path(__file__).parent.parent / "data" / "reading.json"
        with open(path, encoding="utf-8") as f:
            _TEXTS = json.load(f)
    return _TEXTS


def _reading_menu_kb() -> InlineKeyboardMarkup:
    levels = [("1", "Начальный"), ("2", "Базовый"), ("3", "Средний")]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Уровень {lvl} — {name}", callback_data=f"reading:level:{lvl}")]
            for lvl, name in levels
        ]
        + [[InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")]]
    )


@router.callback_query(lambda c: c.data == "section:reading")
async def reading_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "📖 *Чтение*\n\nВыберите уровень сложности:",
        reply_markup=_reading_menu_kb(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("reading:level:"))
async def reading_level(callback: CallbackQuery) -> None:
    level = int(callback.data.split(":")[2])
    texts = [t for t in _load() if t["level"] == level]

    if not texts:
        await callback.answer("Тексты этого уровня скоро появятся.", show_alert=True)
        return

    text_data = texts[0]
    text = (
        f"📖 *{text_data['title']}*\n\n"
        f"{text_data['arabic']}\n\n"
        f"_Транскрипция:_\n{text_data['transliteration']}\n\n"
        f"*Перевод:* ||{text_data['translation']}||"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_home_kb("section:reading", "← К чтению"),
        parse_mode="Markdown",
    )
    await callback.answer()
