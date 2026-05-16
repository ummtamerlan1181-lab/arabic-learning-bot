import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from services.ai_service import ask
from states import AIState

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(lambda c: c.data == "section:ai")
async def ai_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIState.waiting)
    await callback.message.edit_text(
        "🤖 *AI-помощник*\n\n"
        "Задайте вопрос по арабскому языку — грамматике, словам, переводу.\n\n"
        "_Введите ваш вопрос:_",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")]]
        ),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(AIState.waiting, F.text)
async def ai_answer(message: Message, state: FSMContext) -> None:
    question = message.text.strip() if message.text else ""
    if not question:
        await message.answer("Пожалуйста, введите текстовый вопрос.")
        return

    thinking = await message.answer("⏳ Думаю...")
    answer = await ask(question)
    await thinking.delete()

    await message.answer(
        answer,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💬 Ещё вопрос", callback_data="section:ai")],
                [InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")],
            ]
        ),
    )
