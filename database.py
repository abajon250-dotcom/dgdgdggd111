import sqlite3
from typing import Optional, List, Dict

DB_NAME = "bot_data.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        # Таблица заявок (добавлено поле rejected_reason)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                phone TEXT,
                service_type TEXT NOT NULL,
                type_choice TEXT,
                status TEXT DEFAULT 'waiting',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                admin_message_id INTEGER,
                channel_message_id INTEGER,
                code TEXT,
                sbp_amount TEXT,
                cancel_reason TEXT,
                sbp_requisites TEXT,
                code_requests_count INTEGER DEFAULT 0,
                rejected_reason TEXT
            )
        """)
        # Таблица пользователей (добавлен banned)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                banned BOOLEAN DEFAULT 0,
                ban_reason TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admin_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id INTEGER,
                action TEXT,
                action_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def add_user(user_id: int, username: str = None):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        conn.execute(
            "UPDATE users SET last_seen = CURRENT_TIMESTAMP, username = COALESCE(?, username) WHERE user_id = ?",
            (username, user_id)
        )

def is_user_banned(user_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return bool(row[0]) if row else False

def get_ban_reason(user_id: int) -> Optional[str]:
    with get_connection() as conn:
        row = conn.execute("SELECT ban_reason FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row[0] if row else None

def ban_user(user_id: int, reason: str = None):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET banned = 1, ban_reason = ? WHERE user_id = ?",
            (reason, user_id)
        )

def unban_user(user_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET banned = 0, ban_reason = NULL WHERE user_id = ?",
            (user_id,)
        )

def get_all_users_with_status() -> List[Dict]:
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT user_id, username, banned, ban_reason FROM users ORDER BY user_id").fetchall()
        return [dict(row) for row in rows]

def reject_application(app_id: int, reason: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE applications SET status = 'rejected', rejected_reason = ? WHERE id = ?",
            (reason, app_id)
        )

def get_apps_by_status(status: str, limit: int = 20) -> List[Dict]:
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM applications WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit)
        ).fetchall()
        return [dict(row) for row in rows]
