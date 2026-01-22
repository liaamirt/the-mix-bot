from dataclasses import dataclass
from aiogram import Bot
import logging
from config import ADMIN_CHAT_ID

@dataclass
class Texts:
    welcome: str = (
        "Привіт! 👋 Вас вітає ресторан <b>The Mix</b>.\n"
        "Оберіть потрібний розділ нижче. Якщо меню зникло — надішліть /start."
    )
    contacts: str = (
        "📍 <b>Адреса</b>: пр. Тараса Шевченка 25, м. Суми\n"
        "🕒 <b>Години</b>: 11:00–21:00\n"
        "📞 <b>Телефон</b>: +380953489333\n"
        "🌐 <b>Соцмережі</b>: Instagram: @themixsumy\n"
        "<b>Завжди чекаємо на Вас у TheMix</b> 🫶"
    )

TEXTS = Texts()

async def notify_admin(bot: Bot, text: str):
    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(ADMIN_CHAT_ID, text)
        except Exception as e:
            logging.warning("Failed to notify admin: %s", e)
