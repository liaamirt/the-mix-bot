from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_kb() -> ReplyKeyboardMarkup:
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
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Так", callback_data=cb_yes),
                InlineKeyboardButton(text="Ні", callback_data=cb_no),
            ]
        ]
    )
