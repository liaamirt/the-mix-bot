from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_kb() -> ReplyKeyboardMarkup:
    """
    Генерує головне навігаційне меню бота.

    Створює та повертає об'єкт `ReplyKeyboardMarkup`, який містить три основні
    навігаційні кнопки, розташовані у два ряди. Клавіатура автоматично масштабується
    під розмір екрану пристрою (`resize_keyboard=True`) та містить підказку
    у полі вводу (`input_field_placeholder`).

    Returns:
        ReplyKeyboardMarkup: Сконфігурований об'єкт клавіатури для відправки користувачу.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Залишити відгук"),
                KeyboardButton(text="🍽️ Забронювати столик"),
            ],
            [KeyboardButton(text="📍 Наші контакти")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть дію…",
    )


def yesno_kb(cb_yes: str, cb_no: str) -> InlineKeyboardMarkup:
    """
    Генерує інлайн-клавіатуру для простого бінарного вибору ("Так" або "Ні").

    Створює та повертає об'єкт `InlineKeyboardMarkup`, що містить один ряд
    із двома кнопками. Кожна кнопка містить відповідний текст та повертає
    передані callback-дані (callback_data) при натисканні користувачем.

    Args:
        cb_yes (str): Дані, що повертаються системі при натисканні кнопки "Так".
        cb_no (str): Дані, що повертаються системі при натисканні кнопки "Ні".

    Returns:
        InlineKeyboardMarkup: Об'єкт інлайн-клавіатури з двома кнопками.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Так", callback_data=cb_yes),
                InlineKeyboardButton(text="Ні", callback_data=cb_no),
            ]
        ]
    )
