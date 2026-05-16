import logging

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from keyboards.main_menu import main_menu_kb
from services.progress_service import get_or_create_user

router = Router()
logger = logging.getLogger(__name__)

WELCOME = (
    "Ассаляму алейкум ва рахматуЛлахи ва баракатух 🌿\n\n"
    "Добро пожаловать в помощник по изучению арабского языка.\n\n"
    "Выберите раздел:"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if not message.from_user:
        return
    await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name or "Пользователь",
    )
    await message.answer(WELCOME, reply_markup=main_menu_kb())


@router.callback_query(lambda c: c.data == "goto:main")
async def goto_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(WELCOME, reply_markup=main_menu_kb())
    await callback.answer()


@router.message(StateFilter(None), F.text, ~F.text.startswith("/"))
async def text_fallback(message: Message) -> None:
    await message.answer(
        "Используйте меню для навигации.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="⌂ Главное меню", callback_data="goto:main")]]
        ),
    )
