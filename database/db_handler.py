import sqlite3
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, db_path="data/bot_database.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    timezone TEXT DEFAULT 'UTC'
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task_text TEXT,
                    remind_at DATETIME,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            conn.commit()

    def add_user(self, user_id, username):
        with self._get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))

    def add_reminder(self, user_id, task_text, remind_at_str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reminders (user_id, task_text, remind_at) VALUES (?, ?, ?)",
                (user_id, task_text, remind_at_str)
            )
            return cursor.lastrowid

    def get_active_reminders(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reminders WHERE status = 'pending'")
            return cursor.fetchall()

    def mark_completed(self, reminder_id):
        with self._get_connection() as conn:
            conn.execute("UPDATE reminders SET status = 'completed' WHERE id = ?", (reminder_id,))

    def delete_reminder(self, reminder_id):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))

    def get_user_reminders(self, user_id):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reminders WHERE user_id = ? AND status = 'pending'", (user_id,))
            return cursor.fetchall()
