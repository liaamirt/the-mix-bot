import aiosqlite
from config import DB_PATH

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    rating INTEGER,
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    date TEXT,
    time TEXT,
    guests INTEGER,
    wishes TEXT,
    phone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_db():
    """
    Ініціалізує базу даних SQLite та створює необхідні таблиці.

    Функція підключається до бази даних за шляхом `DB_PATH`, який імпортується
    з конфігураційного модуля. Якщо таблиці `feedbacks` та `bookings` ще не існують,
    вони автоматично створюються за допомогою виконання SQL-скрипта `CREATE_TABLES_SQL`.
    Використання асинхронного контекстного менеджера гарантує безпечне закриття
    з'єднання з базою даних навіть у випадку виникнення непередбачених помилок.

    Raises:
        aiosqlite.Error: Виникає у разі проблем із доступом до файлу бази даних
                         або помилок синтаксису SQL.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()


async def add_feedback(user_id, username, rating, comment):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO feedbacks (user_id, username, rating, comment) VALUES (?,?,?,?)",
            (user_id, username, rating, comment),
        )
        await db.commit()


async def add_booking(user_id, username, data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bookings (user_id, username, date, time, guests, wishes, phone) VALUES (?,?,?,?,?,?,?)",
            (
                user_id,
                username,
                data.get("date"),
                data.get("time"),
                int(data.get("guests", 1)),
                data.get("wishes", ""),
                data.get("phone"),
            ),
        )
        await db.commit()
