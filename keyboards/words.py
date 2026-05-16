from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

WORD_THEMES = [
    ("family", "Семья"),
    ("home", "Дом"),
    ("food", "Еда"),
    ("quran", "Коран"),
    ("greetings", "Приветствия"),
    ("study", "Учёба"),
]


def words_menu_kb() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="⭐ Слово дня", callback_data="words:daily")]]
    rows += [
        [InlineKeyboardButton(text=f"📚 {label}", callback_data=f"words:theme:{key}")]
        for key, label in WORD_THEMES
    ]
    rows.append([InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def word_card_kb(word_id: str, theme: str, has_next: bool = True) -> InlineKeyboardMarkup:
    rows = []
    if has_next:
        rows.append([InlineKeyboardButton(
            text="→ Следующее слово",
            callback_data=f"words:next:{theme}:{word_id}"
        )])
    rows.append([InlineKeyboardButton(text="← К темам", callback_data="section:words")])
    rows.append([InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
