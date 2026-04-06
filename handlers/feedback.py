"""
Модуль обробки процесу залишення відгуку клієнтом.

Цей модуль містить роутер та обробники повідомлень (handlers) для
машини станів (FSM), які відповідають за збір оцінки та текстового коментаря
від користувача, збереження їх у базу даних та сповіщення адміністратора.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import FeedbackSG
from keyboards import main_kb
from database import add_feedback
from utils import notify_admin

#: Екземпляр роутера для маршрутизації подій, пов'язаних із відгуками.
router = Router()


@router.message(F.text == "📝 Залишити відгук")
async def feedback_entry(message: Message, state: FSMContext) -> None:
    """
    Ініціює процес залишення відгуку та переводить систему у стан очікування оцінки.

    Обробляє натискання кнопки "📝 Залишити відгук" з головного меню.
    Функція очищує попередній стан машини станів (щоб уникнути конфліктів)
    та запитує у користувача числову оцінку візиту.

    Args:
        message (Message): Об'єкт повідомлення від користувача.
        state (FSMContext): Контекст машини станів aiogram.

    Returns:
        None
    """
    await state.clear()
    await state.set_state(FeedbackSG.waiting_rating)
    await message.answer("Оцініть візит від 1 до 5 ⭐", reply_markup=None)


@router.message(FeedbackSG.waiting_rating)
async def feedback_rating_received(message: Message, state: FSMContext) -> None:
    """
    Обробляє введену користувачем оцінку та перевіряє її валідність.

    Функція намагається перетворити текст повідомлення на ціле число та перевіряє,
    чи знаходиться воно в межах від 1 до 5. Якщо оцінка валідна, вона зберігається
    в тимчасовій пам'яті FSM, а користувач переводиться у стан очікування коментаря.
    У разі помилки вводу (не число або число поза діапазоном), бот просить
    ввести дані повторно.

    Args:
        message (Message): Об'єкт повідомлення, що містить введену оцінку.
        state (FSMContext): Поточний контекст машини станів.

    Returns:
        None
    """
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
async def feedback_comment_received(message: Message, state: FSMContext) -> None:
    """
    Обробляє текстовий коментар користувача та завершує процес збору відгуку.

    Отримує збережену раніше оцінку з контексту FSM та поточний коментар
    із повідомлення. Зберігає зібрані дані в базу даних SQLite за допомогою
    функції `add_feedback`, надсилає користувачу повідомлення з подякою та
    повертає головне меню. Також формує та надсилає сповіщення адміністратору
    про отримання нового відгуку.

    Args:
        message (Message): Об'єкт повідомлення, що містить текст коментаря.
        state (FSMContext): Поточний контекст машини станів.

    Returns:
        None
    """
    comment = message.text.strip()
    data = await state.get_data()
    rating = data.get("rating")

    await add_feedback(
        message.from_user.id, message.from_user.username, rating, comment
    )

    await message.answer(
        f"Дякуємо за ваш відгук! Він буде переданий адміністратору 🥰\nОцінка: {rating} ⭐\nВідгук: {comment}",
        reply_markup=main_kb(),
    )

    admin_text = f"📥 <b>Новий відгук</b>\nВід: @{message.from_user.username}\nОцінка: {rating}\nВідгук: {comment}"
    await notify_admin(message.bot, admin_text)
    await state.clear()
