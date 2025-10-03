from flask import Flask, render_template
import pandas as pd # Import the pandas library

# Initialize the Flask app
app = Flask(__name__, static_folder='assets')

# --- Load the dataset ---
# This code runs once when the application starts.
try:
    data = pd.read_csv('data/symptom_dataset.csv')
    print("Dataset loaded successfully!")
    # Print the first 5 rows to the terminal to verify
    print(data.head()) 
except Exception as e:
    print(f"Error loading dataset: {e}")
    data = None
# -------------------------

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
    app.run(debug=True)
