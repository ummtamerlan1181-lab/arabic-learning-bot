import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from keyboards.common import back_home_kb
from keyboards.words import WORD_THEMES, word_card_kb, words_menu_kb
from services.word_service import get_by_theme, get_daily, get_next

router = Router()
logger = logging.getLogger(__name__)


def _fmt(word: dict) -> str:
    return (
        f"🔤 *{word['arabic']}*\n"
        f"_{word['transliteration']}_\n\n"
        f"📖 {word['translation']}\n\n"
        f"*Пример:*\n"
        f"{word['example_arabic']}\n"
        f"_{word['example_transliteration']}_\n"
        f"{word['example_translation']}"
    )


@router.callback_query(lambda c: c.data == "section:words")
async def words_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🧠 *Слова*\n\nВыберите раздел или тему:",
        reply_markup=words_menu_kb(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "words:daily")
async def word_daily(callback: CallbackQuery) -> None:
    word = get_daily()
    await callback.message.edit_text(
        "⭐ *Слово дня*\n\n" + _fmt(word),
        reply_markup=back_home_kb("section:words", "← К словам"),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("words:theme:"))
async def words_theme(callback: CallbackQuery) -> None:
    theme = callback.data.split(":")[2]
    words = get_by_theme(theme)
    theme_name = dict(WORD_THEMES).get(theme, theme)

    if not words:
        await callback.answer("Слова этой темы скоро появятся.", show_alert=True)
        return

    word = words[0]
    text = f"📚 *{theme_name}* — слово 1 из {len(words)}\n\n" + _fmt(word)
    await callback.message.edit_text(
        text,
        reply_markup=word_card_kb(word["id"], theme, has_next=len(words) > 1),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("words:next:"))
async def words_next(callback: CallbackQuery) -> None:
    parts = callback.data.split(":", 3)
    theme, current_id = parts[2], parts[3]
    words = get_by_theme(theme)
    theme_name = dict(WORD_THEMES).get(theme, theme)
    next_word = get_next(theme, current_id)

    if not next_word:
        await callback.answer("Это последнее слово в теме.", show_alert=True)
        return

    ids = [w["id"] for w in words]
    idx = ids.index(next_word["id"])
    text = f"📚 *{theme_name}* — слово {idx + 1} из {len(words)}\n\n" + _fmt(next_word)
    await callback.message.edit_text(
        text,
        reply_markup=word_card_kb(next_word["id"], theme, has_next=idx + 1 < len(words)),
        parse_mode="Markdown",
    )
    await callback.answer()
