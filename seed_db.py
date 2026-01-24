import sqlite3
import os

DB_NAME = "themix.db"

def seed_database():
    # 1. Видалення старої бази
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"♻️ Старий файл {DB_NAME} видалено.")

    # 2. Підключення та створення таблиць
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Створення таблиці bookings
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

    # Створення таблиці feedbacks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rating INTEGER,
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Наповнення даними (Seeds)
    bookings_data = [
        (111111, "25-12-2025", "18:00", 2, "+380501234567", "Біля вікна"),
        (222222, "01-01-2026", "21:00", 20, "+380999999999", "Ювілей, 5 дитячих стільців"),
        (333333, "08-03-2026", "11:00", 1, "+380630000000", "-"),
        (444444, "14-02-2026", "19:30", 2, "+380971112233", "Love is in the air!")
    ]
    cursor.executemany("INSERT INTO bookings (user_id, date, time, guests, phone, wishes) VALUES (?, ?, ?, ?, ?, ?)", bookings_data)

    feedbacks_data = [
        (111111, 5, "Все супер, кухня смачна!"),
        (222222, 1, "Жахливо. Чекали 40 хвилин."),
        (333333, 3, "Нормально."),
        (444444, 5, "Дуже довгий і детальний відгук про те, як все було чудово...")
    ]
    cursor.executemany("INSERT INTO feedbacks (user_id, rating, comment) VALUES (?, ?, ?)", feedbacks_data)

    conn.commit()
    conn.close()
    print("✅ База даних успішно заповнена seed-даними!")

if __name__ == "__main__":
    seed_database()