from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path

app = Flask(__name__, static_folder='assets')
app.secret_key = "replace_this_with_a_random_secret"  # change to a secure random string in production

DB_PATH = Path("database/users.db")

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
            # set session
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------- protected dashboard ----------
def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.route('/dashboard')
@login_required
def dashboard():
    # show basic dashboard and recent results
    db = get_db()
    rows = db.execute("SELECT * FROM results WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
                      (session['user_id'],)).fetchall()
    return render_template('dashboard.html', results=rows)

# ---------- protected chatbot ----------
@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')


# ---------- save a sample result endpoint ----------
# Example of how to save a symptom-check result (POST from your symptom form)
@app.route('/save_result', methods=['POST'])
@login_required
def save_result():
    # expect JSON or form fields: module, input_data, prediction, risk_score
    module = request.form.get('module') or request.json.get('module')
    input_data = request.form.get('input_data') or request.json.get('input_data')
    prediction = request.form.get('prediction') or request.json.get('prediction')
    risk_score = request.form.get('risk_score') or request.json.get('risk_score')

    db = get_db()
    db.execute(
        "INSERT INTO results (user_id, module, input_data, prediction, risk_score) VALUES (?, ?, ?, ?, ?)",
        (session['user_id'], module, input_data, prediction, float(risk_score) if risk_score else None)
    )
    db.commit()
    return {"status": "ok"}, 201

# ---------- logout ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
