import sqlite3
from typing import Optional, List, Dict

DB_NAME = "bot_data.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")  # Включаем WAL-режим для стабильности и скорости
    return conn

def init_db():
    """Инициализация базы данных и создание таблиц"""
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
                full_name TEXT,
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
        conn.commit()

def add_user(user_id: int, username: str = None, full_name: str = None):
    """Добавление или обновление пользователя в базе"""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, username, full_name, is_banned) 
            VALUES (?, ?, ?, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(?, username),
                full_name = COALESCE(?, full_name),
                last_seen = CURRENT_TIMESTAMP
            """,
            (user_id, username, full_name, username, full_name)
        )
        conn.commit()

def get_user_banned(user_id: int) -> bool:
    """Проверка, заблокирован ли пользователь"""
    with get_connection() as conn:
        row = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            return False
        return bool(row[0])

def get_all_users() -> List[int]:
    """Получение списка ID всех незаблокированных пользователей"""
    with get_connection() as conn:
        rows = conn.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
        return [row[0] for row in rows]

def ban_user(user_id: int):
    """Блокировка пользователя"""
    with get_connection() as conn:
        conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
        conn.commit()

def unban_user(user_id: int):
    """Разблокировка пользователя"""
    with get_connection() as conn:
        conn.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
        conn.commit()

def create_application(user_id: int, username: str, phone: Optional[str], service_type: str, type_choice: str) -> int:
    """Создание новой заявки"""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications (user_id, username, phone, service_type, type_choice, status, code_requests_count) 
            VALUES (?, ?, ?, ?, ?, 'waiting', 0)
            """,
            (user_id, username, phone, service_type, type_choice)
        )
        conn.commit()
        return cursor.lastrowid

def update_app(app_id: int, **kwargs):
    """Динамическое обновление полей заявки"""
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
        conn.commit()

def get_app(app_id: int) -> Optional[Dict]:
    """Получение заявки по ID в виде словаря"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
        return dict(row) if row else None

def get_apps(limit: int = 20, offset: int = 0) -> List[Dict]:
    """Получение списка заявок с пагинацией"""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        return [dict(row) for row in rows]

def get_stats() -> Dict:
    """Получение общей статистики по заявкам"""
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

# Автоматически инициализируем базу данных при импорте модуля
init_db()