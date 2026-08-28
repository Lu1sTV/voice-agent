import hashlib
import secrets
import sqlite3
import uuid
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "voice.db"

MOCK_VERIFICATION_CODE = "123456"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100_000
    ).hex()

    return f"{salt}${password_hash}"


def init_db():
    DATA_DIR.mkdir(exist_ok=True)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            account_locked INTEGER NOT NULL DEFAULT 0,
            password_hash TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verifications (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            verified INTEGER NOT NULL DEFAULT 0,
            verification_token TEXT,
            used INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO users (
            username,
            display_name,
            account_locked,
            password_hash
        )
        VALUES (?, ?, ?, ?)
    """, (
        "max.mustermann",
        "Max Mustermann",
        0,
        hash_password("InitialPassword123")
    ))

    cursor.execute("""
        INSERT OR IGNORE INTO users (
            username,
            display_name,
            account_locked,
            password_hash
        )
        VALUES (?, ?, ?, ?)
    """, (
        "anna.schmidt",
        "Anna Schmidt",
        1,
        hash_password("InitialPassword123")
    ))

    connection.commit()
    connection.close()


def get_user_by_username(username: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            display_name,
            account_locked
        FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    connection.close()

    return user


def get_user_by_id(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            display_name,
            account_locked
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cursor.fetchone()

    connection.close()

    return user


def create_verification(user_id: int):
    verification_id = str(uuid.uuid4())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO verifications (
            id,
            user_id,
            code
        )
        VALUES (?, ?, ?)
    """, (
        verification_id,
        user_id,
        MOCK_VERIFICATION_CODE
    ))

    connection.commit()
    connection.close()

    return verification_id


def confirm_verification(
    verification_id: str,
    code: str
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM verifications
        WHERE id = ?
    """, (verification_id,))

    verification = cursor.fetchone()

    if verification is None:
        connection.close()
        return None

    if verification["used"]:
        connection.close()
        return None

    if verification["code"] != code:
        connection.close()
        return None

    verification_token = secrets.token_urlsafe(32)

    cursor.execute("""
        UPDATE verifications
        SET
            verified = 1,
            verification_token = ?
        WHERE id = ?
    """, (
        verification_token,
        verification_id
    ))

    connection.commit()
    connection.close()

    return verification_token


def reset_password(
    user_id: int,
    verification_token: str,
    new_password: str
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM verifications
        WHERE user_id = ?
          AND verification_token = ?
          AND verified = 1
          AND used = 0
    """, (
        user_id,
        verification_token
    ))

    verification = cursor.fetchone()

    if verification is None:
        connection.close()
        return False

    new_password_hash = hash_password(new_password)

    cursor.execute("""
        UPDATE users
        SET
            password_hash = ?,
            account_locked = 0
        WHERE id = ?
    """, (
        new_password_hash,
        user_id
    ))

    cursor.execute("""
        UPDATE verifications
        SET used = 1
        WHERE id = ?
    """, (
        verification["id"],
    ))

    connection.commit()
    connection.close()

    return True
