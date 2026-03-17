from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# ---------------- DB CONNECTION ----------------
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            ssl_disabled=False
        )
    except Exception as e:
        print("DB ERROR:", e)
        return None

# ---------------- PAGES ----------------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

# ---------------- API: REGISTER ----------------
@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "DB connection failed"}), 500

        cursor = conn.cursor()

        query = """
        INSERT INTO students (name, email, password, department, semester)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data["name"],
            data["email"],
            data["password"],
            data["department"],
            data["semester"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Registered successfully"}), 200

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"error": str(e)}), 500

# ---------------- API: LOGIN ----------------
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "DB connection failed"}), 500

        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM students WHERE email=%s AND password=%s"
        cursor.execute(query, (data["email"], data["password"]))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return jsonify({"message": "Login success"}), 200
        else:
            return jsonify({"error": "Invalid login"}), 401

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": str(e)}), 500

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
