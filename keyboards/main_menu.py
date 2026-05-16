from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📘 Уроки", callback_data="section:lessons")],
            [InlineKeyboardButton(text="🧠 Слова", callback_data="section:words")],
            [InlineKeyboardButton(text="✍️ Упражнения", callback_data="section:exercises")],
            [InlineKeyboardButton(text="📖 Чтение", callback_data="section:reading")],
            [InlineKeyboardButton(text="🎯 Тесты", callback_data="section:tests")],
            [
                InlineKeyboardButton(text="📊 Прогресс", callback_data="section:progress"),
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="section:settings"),
            ],
            [InlineKeyboardButton(text="🤖 Спросить AI", callback_data="section:ai")],
        ]
    )
