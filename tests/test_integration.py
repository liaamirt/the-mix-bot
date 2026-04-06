import pytest
import sys
import os

# Додавання шляху до кореневої папки для доступу до модулів проєкту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from seed_db import BOOKINGS_DATA, FEEDBACKS_DATA

#: Активація асинхронного режиму для всіх тестів у модулі
pytestmark = pytest.mark.asyncio


async def test_seed_bookings_integrity(db_connection):
    """
    Перевіряє цілісність початкових даних (seed) у таблиці бронювань.

    GIVEN: База даних SQLite в пам'яті, наповнена даними з `BOOKINGS_DATA`.
    WHEN:  Виконується вибірка (SELECT) за ідентифікатором першого запису.
    THEN:  Отримані дані (ID та номер телефону) повністю збігаються з
           оригінальним джерелом у файлі seed_db.py.
    """
    expected_booking = BOOKINGS_DATA
    booking_id = expected_booking

    async with db_connection.execute(
        "SELECT * FROM bookings WHERE id =?", (booking_id,)
    ) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        assert row == booking_id
        assert row[1] == expected_booking[1]


async def test_seed_feedbacks_integrity(db_connection):
    """
    Перевіряє коректність збереження та зчитування відгуків користувачів.

    GIVEN: База даних ініціалізована набором тестових відгуків `FEEDBACKS_DATA`.
    WHEN:  Запитується рейтинг та коментар за конкретним ID відгуку.
    THEN:  Значення рейтингу та тексту коментаря відповідають тим,
           що були внесені під час ініціалізації.
    """
    expected_feedback = FEEDBACKS_DATA

    async with db_connection.execute(
        "SELECT rating, comment FROM feedbacks WHERE id =?", (expected_feedback,)
    ) as cursor:
        row = await cursor.fetchone()
        assert row == expected_feedback[2]
        assert row[3] == expected_feedback[4]


async def test_create_new_booking(db_connection):
    """
    Перевіряє успішне створення нового запису про бронювання столика.

    GIVEN: Чисте середовище бази даних (фікстура `db_connection`) та набір
           валідних даних для нового клієнта.
    WHEN:  Система виконує асинхронний SQL-запит INSERT для фіксації бронювання.
    THEN:  Запис успішно з'являється в базі даних, а збережена дата візиту
           залишається незмінною та доступною для пошуку.
    """
    new_booking = (999, "31-12-2025", "23:00", 5, "+380000000000", "New Year")

    await db_connection.execute(
        "INSERT INTO bookings (user_id, date, time, guests, phone, wishes) VALUES (?,?,?,?,?,?)",
        new_booking,
    )
    await db_connection.commit()

    async with db_connection.execute(
        "SELECT * FROM bookings WHERE user_id = 999"
    ) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        assert row[2] == "31-12-2025"


async def test_create_new_feedback(db_connection):
    """
    Перевіряє механізм збереження оцінки якості обслуговування.

    GIVEN: Ізольована БД та дані відгуку (ID користувача, оцінка 4, коментар).
    WHEN:  Дані вставляються в таблицю `feedbacks`.
    THEN:  При запиті по ID користувача система повертає саме ту оцінку,
           яка була надана, підтверджуючи коректність роботи логіки БД.
    """
    new_feedback = (888, 4, "Good service")

    await db_connection.execute(
        "INSERT INTO feedbacks (user_id, rating, comment) VALUES (?,?,?)",
        new_feedback,
    )
    await db_connection.commit()

    async with db_connection.execute(
        "SELECT rating FROM feedbacks WHERE user_id = 888"
    ) as cursor:
        row = await cursor.fetchone()
        assert row == 4


async def test_booking_auto_increment(db_connection):
    """
    Перевіряє правильність роботи механізму автоматичної нумерації (Auto Increment).

    GIVEN: База даних, що вже містить 4 початкових записи (seeds).
    WHEN:  Додається нове бронювання без явного вказання первинного ключа (ID).
    THEN:  SQLite автоматично присвоює новому запису ID = 5, що гарантує
           унікальність та послідовність ідентифікаторів у системі.
    """
    await db_connection.execute(
        "INSERT INTO bookings (user_id, date) VALUES (101, '01-01-2027')"
    )
    await db_connection.commit()

    async with db_connection.execute(
        "SELECT id FROM bookings WHERE user_id = 101"
    ) as cursor:
        row = await cursor.fetchone()
        assert row == 5


async def test_get_bookings_by_phone(db_connection):
    """
    Перевіряє логіку пошуку бронювань за контактним номером телефону.

    GIVEN: Наявність існуючих записів у базі даних.
    WHEN:  Виконується пошук за номером телефону "+380501234567".
    THEN:  Система знаходить та повертає саме те бронювання, якому
           належить цей номер, забезпечуючи роботу фільтрації даних.
    """
    target_phone = BOOKINGS_DATA[1]

    async with db_connection.execute(
        "SELECT id FROM bookings WHERE phone =?", (target_phone,)
    ) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        assert row == BOOKINGS_DATA
