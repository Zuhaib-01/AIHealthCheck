from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Initialize the Flask app
app = Flask(__name__, static_folder='assets')

# --- 1. Load, Prepare, and Train the Model (This runs once at startup) ---
try:
    data = pd.read_csv('data/symptom_dataset.csv')
    
    # Keep a list of the original column names for the symptoms
    symptom_columns = data.columns[:-1].tolist()

    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    le = LabelEncoder()
    y = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)
    print("Model trained successfully!")

except Exception as e:
    print(f"Error during model training: {e}")

# --- 2. Define Web Routes ---
@app.route('/')
def index():
    """Renders the home page and passes the list of symptoms."""
    # The symptom_columns list was created during the data loading phase
    return render_template('index.html', symptoms=symptom_columns)

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint to get a prediction from the model."""
    try:
        # Get symptoms from the POST request
        user_symptoms_raw = request.json.get('symptoms')
        if not user_symptoms_raw:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        # Process the input string into a list of symptoms
        user_symptoms = [s.strip().lower().replace(' ', '_') for s in user_symptoms_raw.split(',')]

        # Create the input vector for the model
        # Start with a vector of all zeros
        input_vector = np.zeros(len(symptom_columns))
        
        # Set the corresponding symptom indices to 1
        for symptom in user_symptoms:
            if symptom in symptom_columns:
                index = symptom_columns.index(symptom)
                input_vector[index] = 1
        
        # Get a prediction from the model
        prediction_index = model.predict([input_vector])[0]
        
        # Convert the prediction index back to the original disease name
        predicted_disease = le.inverse_transform([prediction_index])[0]
        
        return jsonify({'prediction': predicted_disease})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
