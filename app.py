from flask import Flask, request, session, g, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
from utils.chatbot import generate_response, load_shared_datasets

BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = BASE_DIR / "database" / "users.db"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"  # built React app (production only)

app = Flask(__name__, static_folder=None)
app.secret_key = "replace_this_with_a_random_secret"  # change to a secure random string in production

# ---------- database ----------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ---------- load datasets once ----------
dfs = load_shared_datasets()

# ---------- auth helper ----------
def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Not authenticated"}), 401
        return view(**kwargs)
    return wrapped_view

def current_user_payload(db=None):
    db = db or get_db()
    user = db.execute("SELECT id, name, email FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if not user:
        return None
    return {"id": user["id"], "name": user["name"], "email": user["email"]}

# =========================================================
#  AUTH API
# =========================================================
@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not (name and email and password):
        return jsonify({"error": "Please fill in all fields."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    pw_hash = generate_password_hash(password)
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, pw_hash)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered. Please use a different email."}), 409

    session.clear()
    session['user_id'] = cur.lastrowid
    session['user_name'] = name
    return jsonify({"user": {"id": cur.lastrowid, "name": name, "email": email}}), 201

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not (email and password):
        return jsonify({"error": "Please enter email and password."}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user and check_password_hash(user['password_hash'], password):
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return jsonify({"user": {"id": user['id'], "name": user['name'], "email": user['email']}})
    return jsonify({"error": "Invalid email or password."}), 401

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"status": "ok"})

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    user = current_user_payload()
    if not user:
        session.clear()
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": user})

# =========================================================
#  CHAT API
# =========================================================
HISTORY_LIMIT = 20

def get_recent_history(db, user_id, limit=HISTORY_LIMIT):
    rows = db.execute(
        '''SELECT message, response, created_at FROM chat_history
           WHERE user_id = ?
           ORDER BY created_at DESC, id DESC
           LIMIT ?''',
        (user_id, limit)
    ).fetchall()
    return list(reversed(rows))

@app.route('/api/chat/history', methods=['GET'])
@login_required
def api_chat_history():
    db = get_db()
    rows = get_recent_history(db, session['user_id'])
    return jsonify({
        "history": [
            {"message": r["message"], "response": r["response"], "created_at": r["created_at"]}
            for r in rows
        ]
    })

@app.route('/api/chat/message', methods=['POST'])
@login_required
def api_chat_message():
    data = request.get_json(silent=True) or {}
    user_input = (data.get('message') or '').strip()
    user_id = session.get('user_id')

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    db = get_db()
    rows = get_recent_history(db, user_id)
    chat_context = "".join(f"User: {row['message']}\nBot: {row['response']}\n" for row in rows)
    prompt = f"{chat_context}\nUser: {user_input}\nBot:"

    response_text, dataset_used = generate_response(prompt, dfs)

    db.execute(
        "INSERT INTO chat_history (user_id, message, response, dataset_used) VALUES (?, ?, ?, ?)",
        (user_id, user_input, response_text, dataset_used)
    )
    db.commit()

    return jsonify({"reply": response_text})

# =========================================================
#  RESULTS API
# =========================================================
@app.route('/api/results', methods=['GET'])
@login_required
def api_results_list():
    db = get_db()
    rows = db.execute(
        "SELECT id, module, input_data, prediction, risk_score, created_at FROM results "
        "WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (session['user_id'],)
    ).fetchall()
    return jsonify({"results": [dict(r) for r in rows]})

@app.route('/api/results', methods=['POST'])
@login_required
def api_results_create():
    data = request.get_json(silent=True) or {}
    module = data.get('module')
    input_data = data.get('input_data')
    prediction = data.get('prediction')
    risk_score = data.get('risk_score')

    db = get_db()
    db.execute(
        "INSERT INTO results (user_id, module, input_data, prediction, risk_score) VALUES (?, ?, ?, ?, ?)",
        (session['user_id'], module, input_data, prediction, float(risk_score) if risk_score else None)
    )
    db.commit()
    return jsonify({"status": "ok"}), 201

# =========================================================
#  SERVE THE BUILT REACT APP (production only)
#  In dev, run the Vite dev server separately (npm run dev) — it proxies
#  /api/* to this Flask server, so these routes are never hit in dev.
# =========================================================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if not FRONTEND_DIST.exists():
        return jsonify({
            "error": "Frontend build not found. Run 'npm run build' in /frontend, "
                     "or use 'npm run dev' for local development."
        }), 501
    target = FRONTEND_DIST / path
    if path and target.exists() and target.is_file():
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
