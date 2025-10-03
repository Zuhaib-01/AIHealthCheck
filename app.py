from flask import Flask, render_template

# Initialize the Flask app
# We specify 'assets' as the static folder name instead of the default 'static'
app = Flask(__name__, static_folder='assets')

@app.route('/')
def index():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/login')
def login():
    """Renders the login page."""
    return render_template('login.html')

@app.route('/signup')
def signup():
    """Renders the signup page."""
    return render_template('signup.html')

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html')

if __name__ == '__main__':
    # Enables debug mode for auto-reloading upon code changes
    app.run(debug=True)
