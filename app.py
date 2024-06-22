from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
from psycopg2 import sql
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import numpy as np
from tensorflow.keras.models import load_model
import json

load_dotenv()

HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASS")

app = Flask(__name__, static_url_path="/assets", static_folder="templates/assets")
app.secret_key = os.getenv("SECRET_KEY")

# Load the trained model
model_path = 'C:/Users/Lilyrae/Documents/Project Stuff/project/project_lstm.h5'  # Update with your actual path
model = load_model(model_path)

prognosis_mapping = {
    0: '(vertigo) Paroymsal Positional Vertigo', 1: 'AIDS', 2: 'Acne', 3: 'Alcoholic hepatitis', 4: 'Allergy',
    5: 'Arthritis', 6: 'Bronchial Asthma', 7: 'Cervical spondylosis', 8: 'Chicken pox', 9: 'Chronic cholestasis',
    10: 'Common Cold', 11: 'Dengue', 12: 'Diabetes ', 13: 'Dimorphic hemmorhoids(piles)', 14: 'Drug Reaction',
    15: 'Fungal infection', 16: 'GERD', 17: 'Gastroenteritis', 18: 'Heart attack', 19: 'Hepatitis B',
    20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 23: 'Hypertension ', 24: 'Hyperthyroidism',
    25: 'Hypoglycemia', 26: 'Hypothyroidism', 27: 'Impetigo', 28: 'Jaundice', 29: 'Malaria', 30: 'Migraine',
    31: 'Osteoarthristis', 32: 'Paralysis (brain hemorrhage)', 33: 'Peptic ulcer diseae', 34: 'Pneumonia',
    35: 'Psoriasis', 36: 'Tuberculosis', 37: 'Typhoid', 38: 'Urinary tract infection', 39: 'Varicose veins',
    40: 'hepatitis A'
}

symptoms_list = ['itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering',
'chills', 'joint_pain', 'stomach_pain', 'acidity', 'ulcers_on_tongue', 'muscle_wasting',
'vomiting', 'burning_micturition', 'spotting_ urination', 'fatigue', 'weight_gain', 'anxiety', 
'cold_hands_and_feets', 'mood_swings', 'weight_loss', 'restlessness', 'lethargy', 'patches_in_throat', 
'irregular_sugar_level', 'cough', 'high_fever', 'sunken_eyes', 'breathlessness', 'sweating', 
'dehydration', 'indigestion', 'headache', 'yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite', 
'pain_behind_the_eyes', 'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever', 
'yellow_urine', 'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload', 'swelling_of_stomach', 
'swelled_lymph_nodes', 'malaise', 'blurred_and_distorted_vision', 'phlegm', 'throat_irritation', 
'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs', 
'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus',
'neck_pain', 'dizziness', 'cramps', 'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels',
'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties', 'excessive_hunger', 
'extra_marital_contacts', 'drying_and_tingling_lips', 'slurred_speech', 'knee_pain', 'hip_joint_pain', 
'muscle_weakness', 'stiff_neck', 'swelling_joints', 'movement_stiffness', 'spinning_movements', 'loss_of_balance', 
'unsteadiness', 'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort', 'foul_smell_of urine', 
'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)', 'depression', 
'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body', 'belly_pain', 'abnormal_menstruation', 
'dischromic _patches', 'watering_from_eyes', 'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum', 
'rusty_sputum', 'lack_of_concentration', 'visual_disturbances', 'receiving_blood_transfusion', 'receiving_unsterile_injections', 
'coma', 'stomach_bleeding', 'distention_of_abdomen', 'history_of_alcohol_consumption', 'fluid_overload', 'blood_in_sputum', 
'prominent_veins_on_calf', 'palpitations', 'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling', 
'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze']

def get_db_connection():
    conn = psycopg2.connect(host=HOST, database=DB_NAME, user=USER, password=PASSWORD)
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "User" (
            id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            gender TEXT,
            email TEXT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "Report" (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES "User"(id),
            user_comments TEXT NOT NULL,
            diagnostic_results TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        gender = request.form["gender"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL(
                'INSERT INTO "User" (full_name, gender, email, username, password) VALUES (%s, %s, %s, %s, %s)'
            ),
            (full_name, gender, email, username, hashed_password),
        )
        conn.commit()
        cursor.close()
        conn.close()

        session["username"] = username

        flash("Registration successful!", "success")
        return redirect(url_for("chatbot"))  
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL('SELECT id, username, password FROM "User" WHERE username = %s'),
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["username"] = user[1]
            session["user_id"] = user[0]  # Save user ID in the session
            flash("Login successful!", "success")
            return redirect(url_for("chatbot"))  
        else:
            flash("Invalid username or password. Please try again.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        user_input = request.json.get("user_input")

        if "hello" in user_input.lower() or "hi" in user_input.lower():
            response = "Hello! Please list your symptoms."
        else:
            symptoms_dict = {symptom.strip(): 1 for symptom in user_input.split(",")}
            input_data = np.zeros((1, 132))
            
            for symptom, value in symptoms_dict.items():
                if symptom in symptoms_list:
                    input_data[0, symptoms_list.index(symptom)] = value
            
            input_data = input_data.reshape((input_data.shape[0], input_data.shape[1], 1))
            prediction = model.predict(input_data)
            predicted_label = np.argmax(prediction, axis=1)[0]
            response = f"The diagnosis is: {prognosis_mapping[predicted_label]}"
        
        return jsonify({"bot_response": response})

    return render_template("chat_design.html", username=username)

@app.route("/profile")
def profile():
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        sql.SQL('SELECT full_name, gender, email, username FROM "User" WHERE username = %s'),
        (username,),
    )
    user_details = cursor.fetchone()
    cursor.execute(
        sql.SQL('SELECT user_comments, diagnostic_results, date FROM "Report" WHERE user_id = (SELECT id FROM "User" WHERE username = %s) ORDER BY date DESC'),
        (username,),
    )
    report = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("profile.html", user_details=user_details, report=report)

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("user_id", None)  # Clear user ID from session
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
