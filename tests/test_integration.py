import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from seed_db import BOOKINGS_DATA, FEEDBACKS_DATA

pytestmark = pytest.mark.asyncio


# Coverage for Manual TC Group 2 (Data Integrity)
async def test_seed_bookings_integrity(db_connection):
    """
    Automates part of TC 2.x: Перевірка цілісності даних.
    Перевіряє, чи коректно база даних зчитує (Read) існуючі бронювання.
    """
    expected_booking = BOOKINGS_DATA[0]
    booking_id = expected_booking[0]

    async with db_connection.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        assert row[0] == booking_id
        assert row[5] == expected_booking[5]


# Coverage for Manual TC Group 3 (Data Integrity)
async def test_seed_feedbacks_integrity(db_connection):
    """
    Automates part of TC 3.x: Перевірка цілісності відгуків.
    Перевіряє коректність збережених рейтингів та коментарів.
    """
    expected_feedback = FEEDBACKS_DATA[0]

    async with db_connection.execute("SELECT rating, comment FROM feedbacks WHERE id = ?",
                                     (expected_feedback[0],)) as cursor:
        row = await cursor.fetchone()
        assert row[0] == expected_feedback[2]
        assert row[1] == expected_feedback[3]


# Coverage for Manual TC 2.10
async def test_create_new_booking(db_connection):
    """
    Automates TC 2.10: Збереження бронювання.
    Перевіряє, чи успішно система записує (Write) нове бронювання в БД.
    """
    new_booking = (999, "31-12-2025", "23:00", 5, "+380000000000", "New Year")

    await db_connection.execute(
        "INSERT INTO bookings (user_id, date, time, guests, phone, wishes) VALUES (?, ?, ?, ?, ?, ?)",
        new_booking
    )
    await db_connection.commit()

    async with db_connection.execute("SELECT * FROM bookings WHERE user_id = 999") as cursor:
        row = await cursor.fetchone()
        assert row is not None
        assert row[2] == "31-12-2025"


# Coverage for Manual TC 3.4
async def test_create_new_feedback(db_connection):
    """
    Automates TC 3.4: Збереження відгуку.
    Перевіряє фіксацію оцінки та коментаря в БД.
    """
    new_feedback = (888, 4, "Good service")

    await db_connection.execute(
        "INSERT INTO feedbacks (user_id, rating, comment) VALUES (?, ?, ?)",
        new_feedback
    )
    await db_connection.commit()

    async with db_connection.execute("SELECT rating FROM feedbacks WHERE user_id = 888") as cursor:
        row = await cursor.fetchone()
        assert row[0] == 4


# Technical Verification (Supports TC 2.5)
async def test_booking_auto_increment(db_connection):
    """
    Automates TC 2.5 (Implementation detail): Перевірка автоінкременту.
    Гарантує, що нові записи не перезаписують існуючі (Primary Key Integrity).
    """
    await db_connection.execute("INSERT INTO bookings (user_id, date) VALUES (101, '01-01-2027')")
    await db_connection.commit()

    async with db_connection.execute("SELECT id FROM bookings WHERE user_id = 101") as cursor:
        row = await cursor.fetchone()
        assert row[0] == 5  # 4 seeds + 1 new


# Coverage for Manual TC 2.8 (Search Logic)
async def test_get_bookings_by_phone(db_connection):
    """
    Automates TC 2.8: Пошук бронювання.
    Перевіряє логіку вибірки (SELECT) за номером телефону.
    """
    target_phone = BOOKINGS_DATA[0][5]

    async with db_connection.execute("SELECT id FROM bookings WHERE phone = ?", (target_phone,)) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        assert row[0] == BOOKINGS_DATA[0][0]