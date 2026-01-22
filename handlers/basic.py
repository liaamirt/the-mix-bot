from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from utils import TEXTS
from keyboards import main_kb

router = Router()

@router.message(CommandStart())
async def on_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(TEXTS.welcome, reply_markup=main_kb())

@router.message(F.text == "📍 Наші контакти")
async def contacts(message: Message):
    await message.answer(TEXTS.contacts, reply_markup=main_kb(), disable_web_page_preview=True)

@router.message(F.text)
async def fallback(message: Message):
    await message.answer("Оберіть дію у меню нижче:", reply_markup=main_kb())
