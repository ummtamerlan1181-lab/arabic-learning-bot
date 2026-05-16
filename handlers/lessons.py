import json
import logging
from pathlib import Path

from aiogram import Router
from aiogram.types import CallbackQuery

from keyboards.common import back_home_kb
from keyboards.lessons import LESSON_CATEGORIES, lesson_list_kb, lesson_view_kb, lessons_menu_kb

router = Router()
logger = logging.getLogger(__name__)

_LESSONS: list = []


def _load() -> list:
    global _LESSONS
    if not _LESSONS:
        path = Path(__file__).parent.parent / "data" / "lessons.json"
        with open(path, encoding="utf-8") as f:
            _LESSONS = json.load(f)
    return _LESSONS


def _by_category(category: str) -> list:
    return [l for l in _load() if l["category"] == category]


def _by_id(lesson_id: str) -> dict | None:
    return next((l for l in _load() if l["id"] == lesson_id), None)


@router.callback_query(lambda c: c.data == "section:lessons")
async def lessons_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "📘 *Уроки*\n\nВыберите раздел:",
        reply_markup=lessons_menu_kb(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("lesson:cat:"))
async def lesson_category(callback: CallbackQuery) -> None:
    category = callback.data.split(":")[2]
    lessons = _by_category(category)
    category_name = dict(LESSON_CATEGORIES).get(category, category)

    if not lessons:
        await callback.answer("Уроки этой категории скоро появятся.", show_alert=True)
        return

    await callback.message.edit_text(
        f"📘 *{category_name}*\n\nВыберите урок:",
        reply_markup=lesson_list_kb(lessons, category),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("lesson:view:"))
async def lesson_view(callback: CallbackQuery) -> None:
    lesson_id = callback.data.split(":")[2]
    lesson = _by_id(lesson_id)

    if not lesson:
        await callback.answer("Урок не найден.", show_alert=True)
        return

    text = f"📘 *{lesson['title']}*\n\n{lesson['content']}"

    if lesson.get("examples"):
        text += "\n\n*Примеры:*"
        for ex in lesson["examples"]:
            text += f"\n• {ex['arabic']} — _{ex['transliteration']}_ — {ex['translation']}"

    await callback.message.edit_text(
        text,
        reply_markup=lesson_view_kb(lesson_id, lesson["category"]),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("lesson:task:"))
async def lesson_task(callback: CallbackQuery) -> None:
    lesson_id = callback.data.split(":")[2]
    lesson = _by_id(lesson_id)

    if not lesson or not lesson.get("mini_task"):
        await callback.answer("Задание недоступно.", show_alert=True)
        return

    task = lesson["mini_task"]
    text = (
        f"✍️ *Мини\\-задание*\n\n"
        f"*Вопрос:* {task['question']}\n\n"
        f"_Подсказка: {task['hint']}_\n\n"
        f"*Ответ:* ||{task['answer']}||"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_home_kb(f"lesson:view:{lesson_id}", "← К уроку"),
        parse_mode="MarkdownV2",
    )
    await callback.answer()
