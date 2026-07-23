import sqlite3
from typing import Optional, List, Dict

DB_NAME = "bot_data.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
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
                code_requests_count INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                is_banned INTEGER DEFAULT 0,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            "INSERT OR IGNORE INTO users (user_id, username, is_banned) VALUES (?, ?, 0)",
            (user_id, username)
        )
        conn.execute(
            "UPDATE users SET last_seen = CURRENT_TIMESTAMP, username = COALESCE(?, username) WHERE user_id = ?",
            (username, user_id)
        )

def get_all_users() -> List[int]:
    with get_connection() as conn:
        # Выбираем только тех, кто не заблокирован
        rows = conn.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
        return [row[0] for row in rows]

def ban_user(user_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))

def unban_user(user_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))

def create_application(user_id: int, username: str, phone: Optional[str], service_type: str, type_choice: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO applications (user_id, username, phone, service_type, type_choice, status, code_requests_count) "
            "VALUES (?, ?, ?, ?, ?, 'waiting', 0)",
            (user_id, username, phone, service_type, type_choice)
        )
        return cursor.lastrowid

def update_app(app_id: int, **kwargs):
    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(app_id)
    if not fields:
        return
    with get_connection() as conn:
        conn.execute(
            f"UPDATE applications SET updated_at = CURRENT_TIMESTAMP, {', '.join(fields)} WHERE id = ?",
            values
        )

def get_app(app_id: int) -> Optional[Dict]:
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
        return dict(row) if row else None

def get_apps(limit: int = 20, offset: int = 0) -> List[Dict]:
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        return [dict(row) for row in rows]

def get_stats() -> Dict:
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        waiting = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'waiting'").fetchone()[0]
        completed = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'completed'").fetchone()[0]
        cancelled = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'cancelled'").fetchone()[0]
        sdat = conn.execute("SELECT COUNT(*) FROM applications WHERE service_type = 'sdat'").fetchone()[0]
        sbp = conn.execute("SELECT COUNT(*) FROM applications WHERE service_type = 'sbp'").fetchone()[0]
        return {
            "total": total,
            "waiting": waiting,
            "completed": completed,
            "cancelled": cancelled,
            "sdat": sdat,
            "sbp": sbp
        }

init_db()