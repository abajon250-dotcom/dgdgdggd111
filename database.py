import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
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
    conn.close()

def create_application(user_id, username, type_choice, service_type, phone):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO applications (user_id, username, type_choice, service_type, phone) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, type_choice, service_type, phone)
    )
    conn.commit()
    app_id = cursor.lastrowid
    conn.close()
    return app_id

def update_app(app_id, **kwargs):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    for key, value in kwargs.items():
        cursor.execute(f"UPDATE applications SET {key} = ? WHERE id = ?", (value, app_id))
    conn.commit()
    conn.close()

def get_app(app_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    conn.close()
    return row