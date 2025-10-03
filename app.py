from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import numpy as np

app = Flask(__name__, static_folder='assets')

# --- 1. Load, Prepare, Train, and Evaluate Model ---
try:
    data = pd.read_csv('data/symptom_dataset.csv')
    symptom_columns = data.columns[:-1].tolist()

    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    le = LabelEncoder()
    y = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

except Exception as e:
    print(f"Error: {e}")

# --- 2. Define Web Routes ---
@app.route('/')
def index():
    return render_template('index.html', symptoms=symptom_columns)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        user_symptoms_raw = request.json.get('symptoms')
        if not user_symptoms_raw:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        user_symptoms = [s.strip().lower().replace(' ', '_') for s in user_symptoms_raw.split(',')]
        input_vector = np.zeros(len(symptom_columns))
        
        for symptom in user_symptoms:
            if symptom in symptom_columns:
                index = symptom_columns.index(symptom)
                input_vector[index] = 1
        
        prediction_index = model.predict([input_vector])[0]
        predicted_disease = le.inverse_transform([prediction_index])[0]
        
        return jsonify({'prediction': predicted_disease})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
