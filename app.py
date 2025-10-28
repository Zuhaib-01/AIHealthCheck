from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
from utils.chatbot import generate_response, load_shared_datasets
import csv
from datetime import datetime
from pathlib import Path


app = Flask(__name__, static_folder='assets')
app.secret_key = "replace_this_with_a_random_secret"  # change to a secure random string in production

# ---------- database setup ----------
BASE_DIR = Path(__file__).parent.resolve()  # AIHealthCheck folder
DB_PATH = BASE_DIR / "database" / "users.db"

def get_db():
    """Establishes a SQLite connection and stores it in Flask's 'g' context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ---------- load datasets once ----------
dfs = load_shared_datasets()

# ---------- public pages ----------
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ---------- signup ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not (name and email and password):
            flash("Please fill in all fields.", "warning")
            return redirect(url_for('signup'))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "warning")
            return redirect(url_for('signup'))

        pw_hash = generate_password_hash(password)
        db = get_db()
        try:
            db.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                       (name, email, pw_hash))
            db.commit()
        except sqlite3.IntegrityError:
            flash("Email already registered. Please use a different email.", "danger")
            return render_template('signup.html', name=name, email=email)

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# ---------- login ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not (email and password):
            flash("Please enter email and password.", "warning")
            return redirect(url_for('login'))

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------- login_required decorator ----------
def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# ---------- dashboard ----------
@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM results WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (session['user_id'],)
    ).fetchall()
    return render_template('dashboard.html', results=rows)

# ---------- chatbot (page) ----------
@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

# ---------- chatbot (AJAX API) ----------
@app.route('/chatbot/message', methods=['POST'])
@login_required
def chatbot_message():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    user_id = session.get("user_id")
    user_name = session.get("user_name")

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    # 📂 Ensure chat_history folder exists
    CHAT_HISTORY_DIR = Path(__file__).parent / "chat_history"
    CHAT_HISTORY_DIR.mkdir(exist_ok=True)

    # 📄 Create per-user CSV file (e.g., chat_user_3.csv)
    chat_file = CHAT_HISTORY_DIR / f"chat_user_{user_id}.csv"

    # 🧠 Read previous chat history (if file exists)
    chat_context = ""
    if chat_file.exists():
        with open(chat_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                chat_context += f"User: {row['message']}\nBot: {row['response']}\n"

    # 🗣 Combine past chats with the new message
    prompt = f"""{chat_context}\nUser: {user_input}\nBot:"""

    # 💡 Generate chatbot response using local datasets
    response_text, dataset_used = generate_response(prompt, dfs)

    # 🧾 Save this new interaction in the user's CSV file
    file_exists = chat_file.exists()
    with open(chat_file, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "message", "response", "dataset_used"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": user_input,
            "response": response_text,
            "dataset_used": dataset_used
        })

    # ✅ Also save to database for reference (optional, can remove)
    db = get_db()
    db.execute('''
        INSERT INTO chat_history (user_id, message, response, dataset_used)
        VALUES (?, ?, ?, ?)
    ''', (user_id, user_input, response_text, dataset_used))
    db.commit()

    return jsonify({"reply": response_text})



# ---------- save a sample result endpoint ----------
@app.route('/save_result', methods=['POST'])
@login_required
def save_result():
    module = request.form.get('module') or request.json.get('module')
    input_data = request.form.get('input_data') or request.json.get('input_data')
    prediction = request.form.get('prediction') or request.json.get('prediction')
    risk_score = request.form.get('risk_score') or request.json.get('risk_score')

    db = get_db()
    db.execute('''
        INSERT INTO results (user_id, module, input_data, prediction, risk_score)
        VALUES (?, ?, ?, ?, ?)
    ''', (session['user_id'], module, input_data, prediction,
          float(risk_score) if risk_score else None))
    db.commit()

    return jsonify({"status": "ok"}), 201

# ---------- logout ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
