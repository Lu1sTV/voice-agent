import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "voice.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    DATA_DIR.mkdir(exist_ok=True)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            account_locked INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO users (
            username,
            display_name,
            account_locked
        )
        VALUES (?, ?, ?)
    """, (
        "max.mustermann",
        "Max Mustermann",
        0
    ))

    cursor.execute("""
        INSERT OR IGNORE INTO users (
            username,
            display_name,
            account_locked
        )
        VALUES (?, ?, ?)
    """, (
        "anna.schmidt",
        "Anna Schmidt",
        1
    ))

    connection.commit()
    connection.close()


def get_user_by_username(username: str):
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, username, display_name, account_locked
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    connection.close()

    return user
