"""
Модуль обробки базових команд та загальних текстових повідомлень.

Цей модуль містить роутер для обробки команди /start, запиту контактної
інформації та резервний обробник (fallback) для будь-якого іншого тексту,
який не підпадає під визначені критерії в інших роутерах.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from utils import TEXTS
from keyboards import main_kb

#: Екземпляр роутера для маршрутизації базових подій бота.
router = Router()


@router.message(CommandStart())
async def on_start(message: Message, state: FSMContext) -> None:
    """
    Обробляє базову команду /start.

    Функція скидає будь-який поточний стан машини станів (FSM), щоб гарантувати
    чистий початок сесії. Після цього надсилає користувачу привітальне повідомлення
    та відображає головне навігаційне меню.

    Args:
        message (Message): Об'єкт повідомлення від користувача, наданий aiogram.
        state (FSMContext): Контекст кінцевого автомата для керування станами.

    Returns:
        None
    """
    await state.clear()
    await message.answer(TEXTS.welcome, reply_markup=main_kb())


@router.message(F.text == "📍 Наші контакти")
async def contacts(message: Message) -> None:
    """
    Відправляє користувачу контактну інформацію ресторану.

    Реагує на натискання кнопки "📍 Наші контакти" з головного меню.
    Вимикає попередній перегляд веб-сторінок для посилань у повідомленні
    (`disable_web_page_preview=True`), щоб повідомлення виглядало охайно
    і не перевантажувало чат зайвими прев'ю Instagram чи Google Maps.

    Args:
        message (Message): Об'єкт повідомлення від користувача.

    Returns:
        None
    """
    await message.answer(
        TEXTS.contacts, reply_markup=main_kb(), disable_web_page_preview=True
    )


@router.message(F.text)
async def fallback(message: Message) -> None:
    """
    Резервний обробник (fallback) для нерозпізнаних текстових повідомлень.

    Цей обробник перехоплює будь-який текст, який не був оброблений попередніми
    фільтрами або іншими роутерами (наприклад, випадковий текст від користувача
    поза процесом бронювання чи залишення відгуку). Він нагадує користувачу про
    необхідність використання кнопок меню.

    Args:
        message (Message): Об'єкт повідомлення з нерозпізнаним текстом.

    Returns:
        None
    """
    await message.answer("Оберіть дію у меню нижче:", reply_markup=main_kb())
