from flask import Flask, render_template, request, jsonify, send_file, redirect, session
import mysql.connector
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import functools

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# ================= DB CONFIG (RENDER SAFE) =================
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME")
        )
    except Exception as e:
        print("DB ERROR:", e)
        return None

# ================= FILE CONFIG =================
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================= LOGIN REQUIRED =================
def login_required(f):
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
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/upload-notes")
def upload_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("upload_notes.html")

@app.route("/view-notes")
def view_notes():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("view_notes.html")

# ================= AUTH =================
@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO students (name, email, password, department, semester)
        VALUES (%s, %s, %s, %s, %s)
        """, (
            data["name"], data["email"], data["password"],
            data["department"], data["semester"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Registered successfully"})
    except Exception as e:
        print(e)
        return jsonify({"error": "Register failed"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    try:
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
            return jsonify({"message": "Login success"})
        else:
            return jsonify({"error": "Invalid login"}), 401
    except Exception as e:
        print(e)
        return jsonify({"error": "Login failed"}), 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= NOTES API =================
@app.route("/api/notes", methods=["GET"])
@login_required
def get_notes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM notes WHERE student_id=%s ORDER BY id DESC",
                   (session["user_id"],))

    notes = cursor.fetchall()
    cursor.close()
    conn.close()

    for n in notes:
        n["upload_date"] = str(n.get("upload_date"))

    return jsonify(notes)


@app.route("/api/upload", methods=["POST"])
@login_required
def upload_note():
    try:
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

        return jsonify({"message": "Uploaded successfully"})
    except Exception as e:
        print(e)
        return jsonify({"error": "Upload failed"}), 500


@app.route("/api/delete/<int:id>", methods=["DELETE"])
@login_required
def delete_note(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id=%s AND student_id=%s",
                   (id, session["user_id"]))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Deleted"})


@app.route("/api/download/<int:id>")
@login_required
def download_note(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT file_name FROM notes WHERE id=%s AND student_id=%s",
                   (id, session["user_id"]))

    note = cursor.fetchone()
    cursor.close()
    conn.close()

    if not note:
        return "File not found", 404

    path = os.path.join(UPLOAD_FOLDER, note["file_name"])
    return send_file(path, as_attachment=True)


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
