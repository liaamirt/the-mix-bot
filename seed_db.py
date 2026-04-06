"""
Модуль для початкового наповнення (seeding) бази даних проєкту.

Цей скрипт створює структуру бази даних SQLite та наповнює її набором
фіксованих тестових даних. Використовується переважно для локальної
розробки, налагодження та забезпечення консистентного стану перед
запуском автоматизованих інтеграційних тестів.
"""

import sqlite3
import os

#: Ім'я файлу локальної бази даних SQLite.
DB_NAME = "themix.db"

# --- Експортовані дані (доступні для тестів) ---

#: Список кортежів із фіксованими тестовими даними для таблиці бронювань.
#: Містить id, user_id, дату, час, кількість гостей, телефон та побажання.
BOOKINGS_DATA = [
    (1, 111111, "25-12-2025", "18:00", 2, "+380501234567", "Біля вікна"),
    (2, 222222, "01-01-2026", "21:00", 20, "+380999999999", "Ювілей"),
    (3, 333333, "08-03-2026", "11:00", 1, "+380630000000", "-"),
    (4, 444444, "14-02-2026", "19:30", 2, "+380971112233", "Love is in the air!"),
]

#: Список кортежів із фіксованими тестовими даними для таблиці відгуків.
#: Містить id, user_id, рейтинг (1-5) та текстовий коментар.
FEEDBACKS_DATA = [
    (1, 111111, 5, "Все супер, кухня смачна!"),
    (2, 222222, 1, "Жахливо. Чекали 40 хвилин."),
    (3, 333333, 3, "Нормально."),
    (4, 444444, 5, "Детальний відгук..."),
]


# -----------------------------------------------


def seed_database() -> None:
    """
    Перестворює базу даних та заповнює її початковими тестовими даними.

    Алгоритм роботи функції:
    1. Перевіряє наявність файлу бази даних (визначеного у `DB_NAME`) і видаляє
       його, якщо він існує, щоб гарантувати повністю чисте середовище.
    2. Встановлює з'єднання з SQLite.
    3. Створює таблиці `bookings` та `feedbacks` із необхідною схемою бази даних.
    4. Вставляє дані з глобальних змінних `BOOKINGS_DATA` та `FEEDBACKS_DATA`
       за допомогою пакетного запиту `executemany()`. Жорстке задання ID записів
       гарантує передбачуваність результатів для перевірок у pytest.
    5. Зберігає зміни (commit) та безпечно закриває з'єднання.

    Returns:
        None
    """
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"♻️ Старий файл {DB_NAME} видалено.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            time TEXT,
            guests INTEGER,
            phone TEXT,
            wishes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rating INTEGER,
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Використовуємо змінні, оголошені вище
    # Важливо: ми вставляємо ID явно, щоб тести знали, який ID очікувати
    cursor.executemany(
        "INSERT INTO bookings (id, user_id, date, time, guests, phone, wishes) VALUES (?,?,?,?,?,?,?)",
        BOOKINGS_DATA,
    )

    cursor.executemany(
        "INSERT INTO feedbacks (id, user_id, rating, comment) VALUES (?,?,?,?)",
        FEEDBACKS_DATA,
    )

    conn.commit()
    conn.close()
    print("✅ База даних успішно заповнена seed-даними!")


if __name__ == "__main__":
    seed_database()
