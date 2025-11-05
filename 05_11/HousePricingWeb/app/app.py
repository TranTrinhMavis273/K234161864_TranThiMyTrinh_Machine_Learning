from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import numpy as np
import os
from datetime import datetime
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics

app = Flask(__name__)
app.secret_key = 'house-secret-key'  # cần để flash message

DATA_PATH = "dataset/USA_Housing.csv"
MODEL_DIR = "model"

# ============ Load Dataset =============
@app.route('/')
def home():
    df = pd.read_csv(DATA_PATH).head(10)
    return render_template('index.html', tables=[df.to_html(classes='table table-striped', index=False)])

# ============ Train Model =============
@app.route('/train', methods=['POST'])
def train_model():
    ratio = float(request.form.get('train_ratio', 0.8))
    df = pd.read_csv(DATA_PATH)

    X = df[['Avg. Area Income', 'Avg. Area House Age', 'Avg. Area Number of Rooms',
            'Avg. Area Number of Bedrooms', 'Area Population']]
    y = df['Price']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1 - ratio, random_state=101)
    lm = LinearRegression()
    lm.fit(X_train, y_train)

    predictions = lm.predict(X_test)
    mae = metrics.mean_absolute_error(y_test, predictions)
    mse = metrics.mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)

    # Lưu model
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"housingmodel_{now}.zip"
    pickle.dump(lm, open(os.path.join(MODEL_DIR, filename), 'wb'))

    flash(f"Model trained & saved as {filename}. MAE={mae:.2f}, RMSE={rmse:.2f}")
    return redirect(url_for('home'))

# ============ Load Models =============
@app.route('/models')
def list_models():
    models = [f for f in os.listdir(MODEL_DIR) if f.endswith(".zip")]
    return render_template('models.html', models=models)

@app.route('/predict', methods=['POST'])
def predict_price():
    model_name = request.form.get('model_name')
    model_path = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(model_path):
        flash("Model file not found.")
        return redirect(url_for('list_models'))

    model = pickle.load(open(model_path, 'rb'))

    try:
        data = [
            float(request.form['income']),
            float(request.form['age']),
            float(request.form['rooms']),
            float(request.form['bedrooms']),
            float(request.form['population'])
        ]
    except ValueError:
        flash("Please input valid numbers.")
        return redirect(url_for('list_models'))

    pred = model.predict([data])[0]
    flash(f"Predicted Price: {pred:,.2f}")
    return redirect(url_for('list_models'))

if __name__ == '__main__':
    os.makedirs(MODEL_DIR, exist_ok=True)
    app.run(debug=True)
