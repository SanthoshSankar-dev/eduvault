from flask import Flask, render_template, request, jsonify, send_file, redirect, session
import mysql.connector
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import functools

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# ================= DB =================
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca="ca.pem",          # ✅ IMPORTANT
        ssl_verify_cert=True
    )
# ================= FILE =================
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================= LOGIN REQUIRED =================
def login_required_page(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

def login_required_api(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401
        return f(*args, **kwargs)
    return wrapper

# ================= PAGES =================
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
@login_required_page
def dashboard():
    return render_template("dashboard.html")

@app.route("/upload-notes")
@login_required_page
def upload_page():
    return render_template("upload_notes.html")

@app.route("/view-notes")
@login_required_page
def view_notes():
    return render_template("view_notes.html")

@app.route("/profile")
@login_required_page
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT name, email, department, semester 
        FROM students WHERE id=%s
    """, (session["user_id"],))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("profile.html", user=user)

# ================= AUTH =================
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students WHERE email=%s AND password=%s",
                   (data["email"], data["password"]))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        session["user_id"] = user["id"]
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Invalid login"}), 401


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= NOTES =================
@app.route("/api/notes")
@login_required_api
def get_notes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM notes WHERE student_id=%s ORDER BY id DESC",
                   (session["user_id"],))

    notes = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(notes)


@app.route("/api/upload", methods=["POST"])
@login_required_api
def upload_note():
    file = request.files.get("file")
    subject = request.form.get("subject")
    title = request.form.get("title")
    description = request.form.get("description")

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    filename = secure_filename(file.filename)
    filename = str(datetime.now().timestamp()) + "_" + filename

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notes (student_id, subject, title, description, file_name)
        VALUES (%s, %s, %s, %s, %s)
    """, (session["user_id"], subject, title, description, filename))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True})


@app.route("/api/delete/<int:id>", methods=["DELETE"])
@login_required_api
def delete_note(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id=%s AND student_id=%s",
                   (id, session["user_id"]))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True})


@app.route("/api/download/<int:id>")
@login_required_api
def download_note(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT file_name FROM notes WHERE id=%s AND student_id=%s",
                   (id, session["user_id"]))

    note = cursor.fetchone()

    cursor.close()
    conn.close()

    if not note:
        return "Not found", 404

    path = os.path.join(UPLOAD_FOLDER, note["file_name"])
    return send_file(path, as_attachment=True)


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
