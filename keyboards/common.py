from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def home_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")]
        ]
    )


def back_home_kb(back_callback: str, back_label: str = "← Назад") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=back_label, callback_data=back_callback)],
            [InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")],
        ]
    )
