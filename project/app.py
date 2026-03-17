from flask import Flask, render_template, request, jsonify, send_file, redirect, session
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import functools

app = Flask(__name__)

# 🔐 Secret key
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

# 📁 Upload config
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
MAX_FILE_SIZE = 50 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 🗄️ DB CONFIG (Aiven / Render ENV)
db_config = {
    'host': os.getenv('mysql-3cda7efb-lcseb02santhoshs-effd.a.aivencloud.com'),
    'port': int(os.getenv('11729', 3306)),
    'user': os.getenv('avnadmin'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('defaultdb'),
    'ssl_disabled': False  # Aiven requires SSL
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except Error as e:
        print("DB Error:", e)
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@app.before_request
def before_request():
    create_upload_folder()

def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'student_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

# ================= AUTH =================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed = generate_password_hash(data['password'])

    try:
        cursor.execute(
            "INSERT INTO students (name,email,password) VALUES (%s,%s,%s)",
            (data['name'], data['email'], hashed)
        )
        conn.commit()
        return jsonify({"message": "Registered"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students WHERE email=%s", (data['email'],))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], data['password']):
        session['student_id'] = user['id']
        session['student_name'] = user['name']
        return jsonify({"message": "Login success"})
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

# ================= ROUTES =================

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload-notes')
@login_required
def upload_notes():
    return render_template('upload_notes.html')

@app.route('/view-notes')
@login_required
def view_notes():
    return render_template('view_notes.html')

# ================= FILE UPLOAD =================

@app.route('/api/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    subject = request.form['subject']
    title = request.form['title']

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file.save(filepath)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO notes (student_id,subject,title,file_name,upload_date) VALUES (%s,%s,%s,%s,%s)",
        (session['student_id'], subject, title, filename, datetime.now().date())
    )
    conn.commit()

    return jsonify({"message": "Uploaded"})

# ================= VIEW NOTES =================

@app.route('/api/notes')
@login_required
def get_notes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM notes WHERE student_id=%s", (session['student_id'],))
    notes = cursor.fetchall()

    return jsonify(notes)

# ================= DOWNLOAD =================

@app.route('/api/download/<int:id>')
@login_required
def download(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM notes WHERE id=%s", (id,))
    note = cursor.fetchone()

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], note['file_name'])

    return send_file(filepath, as_attachment=True)

# ================= RUN =================

if __name__ == "__main__":
    create_upload_folder()
    app.run(host="0.0.0.0", port=10000)
