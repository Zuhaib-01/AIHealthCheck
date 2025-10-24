import sqlite3
from pathlib import Path

DB_PATH = Path("database/users.db")
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# optional: results table to store user symptom checks / predictions
c.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    module TEXT,
    input_data TEXT,
    prediction TEXT,
    risk_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
''')

conn.commit()
conn.close()
print("✅ Database & tables created at", DB_PATH)
