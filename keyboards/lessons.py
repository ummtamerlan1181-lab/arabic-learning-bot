from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

LESSON_CATEGORIES = [
    ("alphabet", "Алфавит"),
    ("reading", "Чтение"),
    ("grammar", "Грамматика"),
    ("verbs", "Глаголы"),
    ("pronouns", "Местоимения"),
    ("prepositions", "Предлоги"),
    ("dialogues", "Диалоги"),
]


def lessons_menu_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"lesson:cat:{key}")]
        for key, label in LESSON_CATEGORIES
    ]
    rows.append([InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lesson_list_kb(lessons: list, category: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"{'✅ ' if l.get('completed') else ''}{l['title']}",
            callback_data=f"lesson:view:{l['id']}"
        )]
        for l in lessons
    ]
    rows.append([InlineKeyboardButton(text="← Назад", callback_data="section:lessons")])
    rows.append([InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lesson_view_kb(lesson_id: str, category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Мини-задание", callback_data=f"lesson:task:{lesson_id}")],
            [InlineKeyboardButton(text="← К урокам", callback_data=f"lesson:cat:{category}")],
            [InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")],
        ]
    )
