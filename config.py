"""
Модуль конфігурації Telegram-бота.

Цей модуль завантажує змінні оточення з файлу `.env` (за допомогою бібліотеки
`dotenv`) та ініціалізує глобальні константи, які використовуються іншими
компонентами проєкту. Також тут виконується базове налаштування системи
логування для відстеження подій у консолі.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

#: str: Секретний токен доступу Telegram-бота, отриманий від BotFather.
BOT_TOKEN = os.getenv("BOT_TOKEN")

#: int: Унікальний ідентифікатор (Chat ID) адміністратора бота.
#: Використовується для надсилання системних сповіщень. За замовчуванням 0.
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

#: str: Шлях до файлу локальної бази даних SQLite.
DB_PATH = "themix.db"

if not BOT_TOKEN:
    print("Warning: BOT_TOKEN is missing in.env")

# Налаштування базового формату та рівня логування системи
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
