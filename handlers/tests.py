import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from services.ai_service import generate_test_questions
from services.progress_service import add_points, save_test_result
from states import TestState

router = Router()
logger = logging.getLogger(__name__)

TEST_TOPICS = [
    ("alphabet", "Алфавит"),
    ("words", "Слова"),
    ("grammar", "Грамматика"),
]


def _tests_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"test:start:{key}")]
            for key, label in TEST_TOPICS
        ]
        + [[InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")]]
    )


def _options_kb(options: list, q_idx: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{chr(65 + i)}. {opt}", callback_data=f"test:answer:{q_idx}:{i}")]
            for i, opt in enumerate(options)
        ]
    )


@router.callback_query(lambda c: c.data == "section:tests")
async def tests_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "🎯 *Тесты*\n\n5 вопросов. AI генерирует тест по выбранной теме.",
        reply_markup=_tests_menu_kb(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("test:start:"))
async def test_start(callback: CallbackQuery, state: FSMContext) -> None:
    topic_key = callback.data.split(":")[2]
    topic_name = dict(TEST_TOPICS).get(topic_key, topic_key)

    await callback.message.edit_text(f"⏳ Генерирую тест по теме «{topic_name}»...")
    questions = await generate_test_questions(topic_name, count=5)

    if not questions:
        await callback.message.edit_text(
            "Не удалось создать тест. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="← Назад", callback_data="section:tests")]]
            ),
        )
        return

    await state.set_state(TestState.in_progress)
    await state.update_data(questions=questions, current=0, score=0, topic=topic_key)
    await _show_question(callback, questions, 0)
    await callback.answer()


async def _show_question(callback: CallbackQuery, questions: list, idx: int) -> None:
    q = questions[idx]
    await callback.message.edit_text(
        f"*Вопрос {idx + 1} из {len(questions)}*\n\n{q['question']}",
        reply_markup=_options_kb(q["options"], idx),
        parse_mode="Markdown",
    )


@router.callback_query(TestState.in_progress, lambda c: c.data and c.data.startswith("test:answer:"))
async def test_answer(callback: CallbackQuery, state: FSMContext) -> None:
    parts = callback.data.split(":")
    q_idx, chosen = int(parts[2]), int(parts[3])

    data = await state.get_data()
    questions = data["questions"]
    score = data["score"]
    q = questions[q_idx]

    if chosen == q["correct"]:
        score += 1
        await callback.answer("✅")
    else:
        await callback.answer(f"❌ {q['options'][q['correct']]}", show_alert=False)

    next_idx = q_idx + 1

    if next_idx < len(questions):
        await state.update_data(current=next_idx, score=score)
        await _show_question(callback, questions, next_idx)
    else:
        topic = data["topic"]
        total = len(questions)
        await state.clear()
        await save_test_result(callback.from_user.id, topic, score, total)
        if score > 0:
            await add_points(callback.from_user.id, score * 15)

        pct = round(score / total * 100)
        emoji = "🏆" if pct >= 80 else "📈" if pct >= 50 else "📚"
        await callback.message.edit_text(
            f"{emoji} *Тест завершён*\n\n"
            f"Результат: *{score} из {total}* ({pct}%)\n\n"
            f"{'Отличная работа!' if pct >= 80 else 'Продолжайте практиковаться — всё придёт с повторением.'}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Пройти ещё раз", callback_data=f"test:start:{topic}")],
                    [InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")],
                ]
            ),
            parse_mode="Markdown",
        )
        await callback.answer()
