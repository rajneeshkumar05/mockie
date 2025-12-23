import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)

    # INTERVIEWS TABLE
    cursor.execute("""
CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_title TEXT,
    job_description TEXT,
    resume_path TEXT,
    final_score INTEGER,
    final_feedback TEXT,
    created_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")


    # QUESTIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER NOT NULL,
        question TEXT,
        answer TEXT,
        score INTEGER,
        feedback TEXT,
        FOREIGN KEY (interview_id) REFERENCES interviews (id)
    )
    """)

    conn.commit()
    conn.close()
