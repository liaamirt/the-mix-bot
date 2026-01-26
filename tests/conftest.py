import pytest
import aiosqlite
import sys
import os

# Додавання шляху до кореневої папки для доступу до seed_db.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from seed_db import BOOKINGS_DATA, FEEDBACKS_DATA


@pytest.fixture
async def db_connection():
    """Фікстура, що створює ізольовану БД в пам'яті та наповнює її даними."""
    async with aiosqlite.connect(":memory:") as db:
        # 1. Ініціалізація схеми БД
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, date TEXT, time TEXT, guests INTEGER, phone TEXT, wishes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, rating INTEGER, comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Наповнення початковими даними (Seeding)
        await db.executemany(
            "INSERT INTO bookings (id, user_id, date, time, guests, phone, wishes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            BOOKINGS_DATA
        )
        await db.executemany(
            "INSERT INTO feedbacks (id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
            FEEDBACKS_DATA
        )
        await db.commit()

        yield db