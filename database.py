import sqlite3

def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                type_choice TEXT,
                service_type TEXT,
                phone TEXT,
                status TEXT DEFAULT 'Ожидание',
                channel_message_id INTEGER
            )
        """)
        conn.commit()

def create_application(user_id, username, type_choice, service_type, phone):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO applications (user_id, username, type_choice, service_type, phone) VALUES (?, ?, ?, ?, ?)", (user_id, username, type_choice, service_type, phone))
        conn.commit()
        return cursor.lastrowid

def update_app(app_id, **kwargs):
    with sqlite3.connect("database.db") as conn:
        for key, value in kwargs.items():
            conn.execute(f"UPDATE applications SET {key} = ? WHERE id = ?", (value, app_id))
        conn.commit()

def get_app(app_id):
    with sqlite3.connect("database.db") as conn:
        return conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()

def get_user_applications(user_id):
    with sqlite3.connect("database.db") as conn:
        return conn.execute("SELECT id, service_type, status FROM applications WHERE user_id = ? ORDER BY id DESC LIMIT 5", (user_id,)).fetchall()