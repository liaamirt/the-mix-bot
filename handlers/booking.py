"""
Модуль обробки процесу бронювання столика.

Цей модуль містить роутер та обробники повідомлень (handlers) для машини
станів (FSM). Він відповідає за покроковий збір інформації від клієнта
(дата, час, кількість гостей, побажання, номер телефону), валідацію введених
даних, збереження їх у базу даних та сповіщення адміністратора.
"""

from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import BookingSG
from keyboards import main_kb
from database import add_booking
from utils import notify_admin

#: Екземпляр роутера для маршрутизації подій процесу бронювання.
router = Router()


@router.message(F.text == "🍽️ Забронювати столик")
async def booking_start(message: Message, state: FSMContext) -> None:
    """
    Ініціює процес бронювання столика та переводить користувача у стан очікування дати.

    Цей асинхронний обробник реагує на конкретне текстове повідомлення від користувача
    ("🍽️ Забронювати столик"). Функція спочатку очищує будь-який попередній стан
    машини станів (FSM), щоб уникнути конфліктів даних, після чого встановлює
    новий стан `BookingSG.waiting_date` та надсилає користувачу інструкцію.

    Args:
        message (Message): Об'єкт повідомлення від користувача, що містить метадані чату,
                           наданий фреймворком aiogram.
        state (FSMContext): Контекст кінцевого автомата для збереження поточного
                            стану сесії користувача.

    Returns:
        None
    """
    await state.clear()
    await state.set_state(BookingSG.waiting_date)
    await message.answer("📅 Вкажіть дату у форматі ДД-ММ-РРРР (наприклад, 06-10-2025)")


@router.message(BookingSG.waiting_date, F.text.regexp(r"^\d{2}-\d{2}-\d{4}$"))
async def booking_date_ok(message: Message, state: FSMContext) -> None:
    """
    Обробляє та валідує введену дату бронювання.

    Перевіряє, чи відповідає дата формату, і чи не є вона в минулому часі.
    Якщо дата коректна, вона зберігається в пам'ять FSM, а система переходить
    до запиту часу. Якщо дата введена неправильно, користувач отримує
    повідомлення про помилку.

    Args:
        message (Message): Об'єкт повідомлення, що містить введену дату.
        state (FSMContext): Поточний контекст машини станів.

    Returns:
        None
    """
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
async def booking_time_ok(message: Message, state: FSMContext) -> None:
    """
    Обробляє та валідує введений час бронювання.

    Перевіряє, чи знаходиться вказаний час у межах робочих годин ресторану
    (між 11:00 та 21:00). За умови успішної перевірки зберігає час і
    запитує кількість гостей.

    Args:
        message (Message): Об'єкт повідомлення, що містить введений час.
        state (FSMContext): Поточний контекст машини станів.

    Returns:
        None
    """
    time = message.text.strip()
    if not (11 <= int(time[:2]) <= 21):
        await message.answer("Час має бути в межах з 11:00 до 21:00.")
        return
    await state.update_data(time=time)
    await state.set_state(BookingSG.waiting_guests)
    await message.answer("👥 Скільки гостей? (цифрою)")


@router.message(BookingSG.waiting_guests, F.text.regexp(r"^\d{1,2}$"))
async def booking_guests_ok(message: Message, state: FSMContext) -> None:
    """
    Обробляє введену кількість гостей.

    Зберігає значення (попередньо перетворивши його на ціле число)
    у контекст FSM і переходить до запиту додаткових побажань.

    Args:
        message (Message): Об'єкт повідомлення з вказаною кількістю гостей.
        state (FSMContext): Поточний контекст машини станів.

    Returns:
        None
    """
    await state.update_data(guests=int(message.text))
    await state.set_state(BookingSG.waiting_wishes)
    await message.answer(
        "🪑 Побажання (місце/подія/дитяче крісло). Якщо немає — напишіть '-' "
    )


@router.message(BookingSG.waiting_wishes)
async def booking_wishes(message: Message, state: FSMContext) -> None:
    """
    Обробляє текстові побажання користувача до бронювання.

    Зберігає текст побажань у стан FSM та переводить систему у фінальний стан
    очікування контактного номеру телефону.

    Args:
        message (Message): Об'єкт повідомлення з текстом побажань.
        state (FSMContext): Поточний контекст машини станів.

    Returns:
        None
    """
    await state.update_data(wishes=message.text)
    await state.set_state(BookingSG.waiting_phone)
    await message.answer("📞 Залиште номер телефону (формат +380XXXXXXXXX)")


@router.message(BookingSG.waiting_phone, F.text.regexp(r"^\+?\d{10,15}$"))
async def booking_phone_ok(message: Message, state: FSMContext) -> None:
    """
    Обробляє номер телефону та фіналізує процес бронювання.

    Витягує всі зібрані дані з пам'яті машини станів, формує запис та
    зберігає його в базу даних SQLite. Після цього відправляє клієнту
    підтвердження, сповіщає адміністратора та скидає стан FSM.

    Args:
        message (Message): Об'єкт повідомлення з контактним номером.
        state (FSMContext): Поточний контекст машини станів.

    Returns:
        None
    """
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
async def booking_guests_fail(message: Message) -> None:
    """
    Обробник некоректного вводу кількості гостей.

    Спрацьовує, якщо користувач вводить дані, які не є числом, під час
    стану очікування кількості гостей. Пропонує правильний формат.

    Args:
        message (Message): Об'єкт повідомлення з помилковим вводом.

    Returns:
        None
    """
    await message.answer("Вкажіть число, наприклад 4")


@router.message(BookingSG.waiting_time)
async def booking_time_fail(message: Message) -> None:
    """
    Обробник некоректного вводу часу бронювання.

    Спрацьовує, якщо користувач вводить час, що не відповідає шаблону ГГ:ХХ.
    Пропонує правильний формат.

    Args:
        message (Message): Об'єкт повідомлення з помилковим вводом.

    Returns:
        None
    """
    await message.answer("Вкажіть час у форматі 19:30")
