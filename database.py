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
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()

async def add_feedback(user_id, username, rating, comment):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO feedbacks (user_id, username, rating, comment) VALUES (?,?,?,?)",
            (user_id, username, rating, comment)
        )
        await db.commit()

async def add_booking(user_id, username, data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bookings (user_id, username, date, time, guests, wishes, phone) VALUES (?,?,?,?,?,?,?)",
            (user_id, username, data.get("date"), data.get("time"), 
             int(data.get("guests", 1)), data.get("wishes", ""), data.get("phone"))
        )
        await db.commit()
