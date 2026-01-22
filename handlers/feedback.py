from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import FeedbackSG
from keyboards import main_kb
from database import add_feedback
from utils import notify_admin

router = Router()

@router.message(F.text == "📝 Залишити відгук")
async def feedback_entry(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(FeedbackSG.waiting_rating)
    await message.answer("Оцініть візит від 1 до 5 ⭐", reply_markup=None)

@router.message(FeedbackSG.waiting_rating)
async def feedback_rating_received(message: Message, state: FSMContext):
    try:
        rating = int(message.text)
        if 1 <= rating <= 5:
            await state.update_data(rating=rating)
            await state.set_state(FeedbackSG.waiting_comment)
            await message.answer("Будь ласка, напишіть ваш відгук:")
        else:
            await message.answer("Будь ласка, вкажіть оцінку від 1 до 5 ⭐")
    except ValueError:
        await message.answer("Будь ласка, вкажіть число від 1 до 5 ⭐")

@router.message(FeedbackSG.waiting_comment)
async def feedback_comment_received(message: Message, state: FSMContext):
    comment = message.text.strip()
    data = await state.get_data()
    rating = data.get("rating")

    await add_feedback(message.from_user.id, message.from_user.username, rating, comment)

    await message.answer(
        f"Дякуємо за ваш відгук! Він буде переданий адміністратору 🥰\nОцінка: {rating} ⭐\nВідгук: {comment}",
        reply_markup=main_kb()
    )

    admin_text = f"📥 <b>Новий відгук</b>\nВід: @{message.from_user.username}\nОцінка: {rating}\nВідгук: {comment}"
    await notify_admin(message.bot, admin_text)
    await state.clear()
