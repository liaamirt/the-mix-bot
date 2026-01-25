import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from seed_db import BOOKINGS_DATA, FEEDBACKS_DATA

pytestmark = pytest.mark.asyncio


# TC-INT-01: Перевірка цілісності даних бронювання
# Мета: Перевірити, що дані, записані Python-скриптом, коректно зчитуються з БД.
async def test_seed_bookings_integrity(db_connection):
    expected_booking = BOOKINGS_DATA[0]
    booking_id = expected_booking[0]

    async with db_connection.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        assert row[0] == booking_id
        assert row[5] == expected_booking[5]  # Перевірка телефону


# TC-INT-02: Перевірка цілісності даних відгуків
# Мета: Перевірити відповідність полів rating та comment після збереження.
async def test_seed_feedbacks_integrity(db_connection):
    expected_feedback = FEEDBACKS_DATA[0]

    async with db_connection.execute("SELECT rating, comment FROM feedbacks WHERE id = ?",
                                     (expected_feedback[0],)) as cursor:
        row = await cursor.fetchone()
        assert row[0] == expected_feedback[2]
        assert row[1] == expected_feedback[3]


# TC-INT-03 (Based on Manual TC 2.10): Створення нового бронювання
# Мета: Перевірити повний цикл запису нового замовлення.
async def test_create_new_booking(db_connection):
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


# TC-INT-04 (Based on Manual TC 3.4): Створення нового відгуку
# Мета: Перевірити запис оцінки та коментаря.
async def test_create_new_feedback(db_connection):
    new_feedback = (888, 4, "Good service")

    await db_connection.execute(
        "INSERT INTO feedbacks (user_id, rating, comment) VALUES (?, ?, ?)",
        new_feedback
    )
    await db_connection.commit()

    async with db_connection.execute("SELECT rating FROM feedbacks WHERE user_id = 888") as cursor:
        row = await cursor.fetchone()
        assert row[0] == 4


# TC-INT-05: Перевірка механізму Auto Increment
# Мета: Перевірити, що БД коректно генерує унікальні ID для нових записів поверх існуючих.
async def test_booking_auto_increment(db_connection):
    # Очікується ID 5 (4 seeds + 1 new)
    await db_connection.execute("INSERT INTO bookings (user_id, date) VALUES (101, '01-01-2027')")
    await db_connection.commit()

    async with db_connection.execute("SELECT id FROM bookings WHERE user_id = 101") as cursor:
        row = await cursor.fetchone()
        assert row[0] == 5


# TC-INT-06: Вибірка даних за критерієм
# Мета: Перевірити роботу SQL-фільтрації (WHERE clause).
async def test_get_bookings_by_phone(db_connection):
    target_phone = BOOKINGS_DATA[0][5]

    async with db_connection.execute("SELECT id FROM bookings WHERE phone = ?", (target_phone,)) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        assert row[0] == BOOKINGS_DATA[0][0]