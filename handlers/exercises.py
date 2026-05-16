import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from services.ai_service import generate_exercise
from services.progress_service import add_points
from states import ExerciseState

router = Router()
logger = logging.getLogger(__name__)


def _options_kb(options: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{chr(65 + i)}. {opt}", callback_data=f"exercise:answer:{i}")]
            for i, opt in enumerate(options)
        ]
        + [[InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")]]
    )


@router.callback_query(lambda c: c.data == "section:exercises")
async def exercises_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "✍️ *Упражнения*\n\nКаждый раз — новое задание, сгенерированное AI.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="▶ Начать упражнение", callback_data="exercise:start")],
                [InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")],
            ]
        ),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "exercise:start")
async def exercise_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("⏳ Генерирую задание...")
    exercise = await generate_exercise()

    if not exercise or not exercise.get("options"):
        await callback.message.edit_text(
            "Не удалось создать задание. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="← Назад", callback_data="section:exercises")]
                ]
            ),
        )
        return

    await state.set_state(ExerciseState.answering)
    await state.update_data(exercise=exercise)

    await callback.message.edit_text(
        f"*{exercise['question']}*\n\nВыберите правильный ответ:",
        reply_markup=_options_kb(exercise["options"]),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(ExerciseState.answering, lambda c: c.data and c.data.startswith("exercise:answer:"))
async def exercise_answer(callback: CallbackQuery, state: FSMContext) -> None:
    chosen = int(callback.data.split(":")[2])
    data = await state.get_data()
    exercise = data.get("exercise", {})
    correct = exercise.get("correct", 0)

    is_correct = chosen == correct
    if is_correct:
        result = "✅ *Правильно!*"
        await add_points(callback.from_user.id, 10)
    else:
        result = f"❌ *Неверно.* Правильный ответ: *{exercise['options'][correct]}*"

    await state.clear()
    await callback.message.edit_text(
        f"{result}\n\n_{exercise.get('explanation', '')}_",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="▶ Ещё упражнение", callback_data="exercise:start")],
                [InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")],
            ]
        ),
        parse_mode="Markdown",
    )
    await callback.answer()
