from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import os

# ✅ FIXED: tell Flask where templates & static are
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "secret123"   # change later

# ---------------- DB CONNECTION ----------------
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            ssl_disabled=False   # for Aiven
        )
    except Exception as e:
        print("DB ERROR:", e)
        return None

# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect("/login")   # ✅ no index.html error

# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.form

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        department = data.get("department")
        semester = data.get("semester")

        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "DB connection failed"})

        cursor = conn.cursor()

        query = """
        INSERT INTO students (name, email, password, department, semester)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, password, department, semester))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"status": "error", "message": str(e)})

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    # ✅ GET → show page
    if request.method == "GET":
        return render_template("login.html")

    # ✅ POST → handle login
    try:
        data = request.form

        email = data.get("email")
        password = data.get("password")

        conn = get_db_connection()
        if not conn:
            return jsonify({"status": "error", "message": "DB connection failed"})

        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM students WHERE email=%s AND password=%s"
        cursor.execute(query, (email, password))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Invalid login"})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"status": "error", "message": str(e)})

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
