from pathlib import Path
import sqlite3

# --- Set project root explicitly ---
PROJECT_ROOT = Path(__file__).parent.parent.resolve()  # parent of utils folder

# --- Database path inside main project folder ---
DB_PATH = PROJECT_ROOT / "database" / "users.db"
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# --- Users table ---
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# --- Results table ---
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
