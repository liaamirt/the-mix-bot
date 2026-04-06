from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import BookingSG
from keyboards import main_kb
from database import add_booking
from utils import notify_admin

router = Router()


@router.message(F.text == "🍽️ Забронювати столик")
async def booking_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BookingSG.waiting_date)
    await message.answer("📅 Вкажіть дату у форматі ДД-ММ-РРРР (наприклад, 06-10-2025)")


@router.message(BookingSG.waiting_date, F.text.regexp(r"^\d{2}-\d{2}-\d{4}$"))
async def booking_date_ok(message: Message, state: FSMContext):
    try:
        booking_date = datetime.strptime(message.text, "%d-%m-%Y")
        if booking_date < datetime.now():
            await message.answer(
                "Неможливо забронювати столик на минулий день. Оберіть майбутню дату."
            )
            return
        await state.update_data(date=message.text)
        await state.set_state(BookingSG.waiting_time)
        await message.answer("🕓 Вкажіть час у форматі ГГ:ХХ (наприклад, 19:30)")
    except ValueError:
        await message.answer("Формат дати невірний.")


@router.message(BookingSG.waiting_time, F.text.regexp(r"^\d{2}:\d{2}$"))
async def booking_time_ok(message: Message, state: FSMContext):
    time = message.text.strip()
    if not (11 <= int(time[:2]) <= 21):
        await message.answer("Час має бути в межах з 11:00 до 21:00.")
        return
    await state.update_data(time=time)
    await state.set_state(BookingSG.waiting_guests)
    await message.answer("👥 Скільки гостей? (цифрою)")


@router.message(BookingSG.waiting_guests, F.text.regexp(r"^\d{1,2}$"))
async def booking_guests_ok(message: Message, state: FSMContext):
    await state.update_data(guests=int(message.text))
    await state.set_state(BookingSG.waiting_wishes)
    await message.answer(
        "🪑 Побажання (місце/подія/дитяче крісло). Якщо немає — напишіть '-' "
    )


@router.message(BookingSG.waiting_wishes)
async def booking_wishes(message: Message, state: FSMContext):
    await state.update_data(wishes=message.text)
    await state.set_state(BookingSG.waiting_phone)
    await message.answer("📞 Залиште номер телефону (формат +380XXXXXXXXX)")


@router.message(BookingSG.waiting_phone, F.text.regexp(r"^\+?\d{10,15}$"))
async def booking_phone_ok(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    user = message.from_user

    await add_booking(user.id, user.username, data)

    summary = (
        "✅ <b>Бронювання надіслано</b>\n"
        f"Дата: {data.get('date')}\nЧас: {data.get('time')}\nГостей: {data.get('guests')}\n"
        f"Телефон: {data.get('phone')}\n"
        "Адміністратор зв'яжеться з Вами."
    )
    await message.answer(summary, reply_markup=main_kb())

    admin_text = (
        f"📥 <b>Нове бронювання</b>\nВід: @{user.username or user.id}\n"
        f"Дата: {data.get('date')} {data.get('time')}\nТелефон: {data.get('phone')}"
    )
    await notify_admin(message.bot, admin_text)
    await state.clear()


@router.message(BookingSG.waiting_guests)
async def booking_guests_fail(message: Message):
    await message.answer("Вкажіть число, наприклад 4")


@router.message(BookingSG.waiting_time)
async def booking_time_fail(message: Message):
    await message.answer("Вкажіть час у форматі 19:30")
