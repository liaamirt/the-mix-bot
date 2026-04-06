import aiosqlite
from config import DB_PATH

#: SQL-скрипт для створення базової структури таблиць бази даних.
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
    """
    Додає новий відгук клієнта до бази даних.

    Асинхронно підключається до БД та виконує SQL-запит INSERT для збереження
    інформації про залишений відгук.

    Args:
        user_id (int): Унікальний ідентифікатор користувача в Telegram.
        username (str): Юзернейм користувача (може бути None, якщо у користувача його немає).
        rating (int): Оцінка візиту, вказана користувачем (зазвичай від 1 до 5).
        comment (str): Текстовий коментар або побажання.

    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO feedbacks (user_id, username, rating, comment) VALUES (?,?,?,?)",
            (user_id, username, rating, comment),
        )
        await db.commit()


async def add_booking(user_id, username, data: dict):
    """
    Зберігає інформацію про нове бронювання столика.

    Функція витягує всі необхідні параметри зі словника `data` (який заповнюється
    через машину станів FSM) та безпечно записує їх у таблицю `bookings`.

    Args:
        user_id (int): Унікальний ідентифікатор користувача в Telegram.
        username (str): Юзернейм користувача.
        data (dict): Словник із даними бронювання. Очікує наявність ключів:
            'date' (str): Дата візиту.
            'time' (str): Час візиту.
            'guests' (int, optional): Кількість гостей. За замовчуванням приводиться до 1.
            'wishes' (str, optional): Додаткові побажання. За замовчуванням порожній рядок.
            'phone' (str): Контактний номер телефону.

    Returns:
        None
    """
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
