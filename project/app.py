from flask import Flask, render_template, request, jsonify, send_file, redirect, session
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import json
import functools

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'vpsanta',  # Change this to your MySQL password
    'database': 'notes_app'
}

def get_db_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    """Create upload folder if it doesn't exist"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@app.before_request
def before_request():
    """Ensure upload folder exists"""
    create_upload_folder()

def login_required(f):
    """Decorator to require login for a route"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# ===== AUTHENTICATION ROUTES =====

@app.route('/api/login', methods=['POST'])
def api_login():
    """Authenticate student and create session"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, email, password, name FROM students WHERE email = %s"
            cursor.execute(query, (email,))
            student = cursor.fetchone()
            cursor.close()
            
            if student and check_password_hash(student['password'], password):
                # Login successful
                session['student_id'] = student['id']
                session['student_email'] = student['email']
                session['student_name'] = student['name']
                
                return jsonify({
                    'message': 'Login successful',
                    'student_id': student['id'],
                    'name': student['name'],
                    'email': student['email']
                }), 200
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
        
        except Error as e:
            print(f"Database error: {e}")
            return jsonify({'error': 'Login failed'}), 500
        finally:
            connection.close()
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register a new student"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        department = data.get('department', '').strip()
        semester = data.get('semester', '').strip()
        
        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            cursor = connection.cursor()
            # Hash password
            hashed_password = generate_password_hash(password)
            
            query = """
                INSERT INTO students (email, password, name, department, semester)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (email, hashed_password, name, department, semester))
            connection.commit()
            cursor.close()
            
            return jsonify({'message': 'Registration successful. Please login.'}), 201
        
        except mysql.connector.errors.IntegrityError:
            return jsonify({'error': 'Email already registered'}), 409
        except Error as e:
            print(f"Database error: {e}")
            return jsonify({'error': 'Registration failed'}), 500
        finally:
            connection.close()
    
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout the student"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/current-student', methods=['GET'])
def get_current_student():
    """Get current logged-in student info"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    return jsonify({
        'student_id': session.get('student_id'),
        'email': session.get('student_email'),
        'name': session.get('student_name')
    }), 200

@app.route('/api/student-stats', methods=['GET'])
def get_student_stats():
    """Get student statistics"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get total notes uploaded
        query_total = "SELECT COUNT(*) as total FROM notes WHERE student_id = %s"
        cursor.execute(query_total, (session['student_id'],))
        total_notes = cursor.fetchone()['total']
        
        # Get unique subjects
        query_subjects = "SELECT COUNT(DISTINCT subject) as subjects FROM notes WHERE student_id = %s"
        cursor.execute(query_subjects, (session['student_id'],))
        unique_subjects = cursor.fetchone()['subjects']
        
        # Get last upload date
        query_last = "SELECT upload_date FROM notes WHERE student_id = %s ORDER BY upload_date DESC LIMIT 1"
        cursor.execute(query_last, (session['student_id'],))
        last_upload_row = cursor.fetchone()
        
        if last_upload_row and last_upload_row['upload_date']:
            last_upload = last_upload_row['upload_date'].strftime('%Y-%m-%d')
        else:
            last_upload = None
        
        cursor.close()
        
        return jsonify({
            'total_notes': total_notes,
            'unique_subjects': unique_subjects,
            'last_upload': last_upload
        }), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error fetching statistics'}), 500
    finally:
        connection.close()

@app.route('/api/subject-stats', methods=['GET'])
def get_subject_stats():
    """Get subjects for current student only"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get subjects for CURRENT STUDENT ONLY with note counts
        query = """
            SELECT subject, COUNT(*) as count
            FROM notes
            WHERE student_id = %s
            GROUP BY subject
            ORDER BY count DESC
            LIMIT 6
        """
        cursor.execute(query, (session['student_id'],))
        subjects = cursor.fetchall()
        cursor.close()
        
        return jsonify(subjects), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error fetching subjects'}), 500
    finally:
        connection.close()

# ===== MODERN UI ROUTES =====

@app.route('/login')
def login():
    """Render the login page"""
    if 'student_id' in session:
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard page"""
    return render_template('dashboard.html')

@app.route('/upload-notes')
@login_required
def upload_notes():
    """Render the upload notes page"""
    return render_template('upload_notes.html')

@app.route('/view-notes')
@login_required
def view_notes():
    """Render the view notes page"""
    return render_template('view_notes.html')

# ===== LEGACY ROUTES =====

@app.route('/')
def index():
    """Redirect to login or dashboard"""
    return redirect('/login')

@app.route('/upload')
def upload_page():
    """Render the legacy upload form page"""
    return render_template('upload.html')

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Get all notes or search by subject"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    search_query = request.args.get('search', '').strip()
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if search_query:
            # Search by subject or title
            query = """
                SELECT id, subject, title, description, file_name, upload_date 
                FROM notes 
                WHERE student_id = %s AND (LOWER(subject) LIKE %s OR LOWER(title) LIKE %s)
                ORDER BY upload_date DESC
            """
            search_param = f"%{search_query.lower()}%"
            cursor.execute(query, (session['student_id'], search_param, search_param))
        else:
            # Get all notes for current student
            query = """
                SELECT id, subject, title, description, file_name, upload_date 
                FROM notes 
                WHERE student_id = %s
                ORDER BY upload_date DESC
            """
            cursor.execute(query, (session['student_id'],))
        
        notes = cursor.fetchall()
        cursor.close()
        
        # Convert dates to string format for JSON serialization
        for note in notes:
            note['upload_date'] = note['upload_date'].strftime('%Y-%m-%d')
        
        return jsonify(notes)
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error fetching notes'}), 500
    finally:
        connection.close()

@app.route('/api/upload', methods=['POST'])
def upload_note():
    """Handle note file upload"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        subject = request.form.get('subject', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate inputs
        if not file or not subject or not title:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Only PDF, TXT, DOC, DOCX are allowed'}), 400
        
        # Secure the filename and create unique name
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + original_filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        
        # Save to database with student_id
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO notes (student_id, subject, title, description, file_name, upload_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (session['student_id'], subject, title, description, filename, datetime.now().date()))
            connection.commit()
            cursor.close()
            
            return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 201
        
        except Error as e:
            print(f"Database error: {e}")
            # Delete file if database insert fails
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': 'Error saving to database'}), 500
        finally:
            connection.close()
    
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/api/download/<int:note_id>', methods=['GET'])
def download_note(note_id):
    """Download a note file - user can only download their own notes"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT file_name, student_id FROM notes WHERE id = %s"
        cursor.execute(query, (note_id,))
        note = cursor.fetchone()
        cursor.close()
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        # Verify user owns this note
        if note['student_id'] != session['student_id']:
            return jsonify({'error': 'Unauthorized - you can only download your own notes'}), 403
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], note['file_name'])
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=note['file_name'])
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error downloading file'}), 500
    finally:
        connection.close()

@app.route('/api/delete/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note"""
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get file name and verify ownership
        query = "SELECT file_name, student_id FROM notes WHERE id = %s"
        cursor.execute(query, (note_id,))
        note = cursor.fetchone()
        
        if not note:
            cursor.close()
            return jsonify({'error': 'Note not found'}), 404
        
        # Check if user owns this note
        if note['student_id'] != session['student_id']:
            cursor.close()
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete from database
        delete_query = "DELETE FROM notes WHERE id = %s"
        cursor.execute(delete_query, (note_id,))
        connection.commit()
        
        # Delete file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], note['file_name'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        cursor.close()
        return jsonify({'message': 'Note deleted successfully'}), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error deleting note'}), 500
    finally:
        connection.close()

# ===== PROFILE ROUTES =====

@app.route('/profile')
@login_required
def profile():
    """Display student profile page"""
    return render_template('profile.html')

@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    """Get student profile data"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id, name, email, department, semester, created_at FROM students WHERE id = %s"
        cursor.execute(query, (session['student_id'],))
        student = cursor.fetchone()
        cursor.close()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify(student), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error fetching profile'}), 500
    finally:
        connection.close()

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update student profile"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        department = data.get('department', '').strip()
        semester = data.get('semester', '').strip()
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        query = "UPDATE students SET name = %s, department = %s, semester = %s WHERE id = %s"
        cursor.execute(query, (name, department, semester, session['student_id']))
        connection.commit()
        cursor.close()
        
        # Update session
        session['student_name'] = name
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error updating profile'}), 500
    finally:
        connection.close()

# ===== ADMIN ROUTES =====

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Admin@123'  # Change this to a secure password

def admin_login_required(f):
    """Decorator to require admin login"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_id'] = 'admin'
            session['admin_username'] = username
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    if 'admin_id' in session:
        return redirect('/admin/dashboard')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_login_required
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return jsonify({'message': 'Logged out'}), 200

@app.route('/api/admin/stats', methods=['GET'])
@admin_login_required
def admin_stats():
    """Get overall platform statistics"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Total students
        cursor.execute("SELECT COUNT(*) as total FROM students")
        total_students = cursor.fetchone()['total']
        
        # Total notes
        cursor.execute("SELECT COUNT(*) as total FROM notes")
        total_notes = cursor.fetchone()['total']
        
        # Total subjects
        cursor.execute("SELECT COUNT(DISTINCT subject) as total FROM notes")
        total_subjects = cursor.fetchone()['total']
        
        # Recent registrations (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) as total FROM students 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        recent_students = cursor.fetchone()['total']
        
        cursor.close()
        
        return jsonify({
            'total_students': total_students,
            'total_notes': total_notes,
            'total_subjects': total_subjects,
            'recent_students': recent_students
        }), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error fetching statistics'}), 500
    finally:
        connection.close()

@app.route('/api/admin/students', methods=['GET'])
@admin_login_required
def admin_get_students():
    """Get all students with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM students")
        total = cursor.fetchone()['total']
        
        # Get paginated students
        query = """
            SELECT id, name, email, department, semester, created_at 
            FROM students 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        students = cursor.fetchall()
        
        # For each student, get note count
        for student in students:
            cursor.execute("SELECT COUNT(*) as count FROM notes WHERE student_id = %s", (student['id'],))
            student['notes_count'] = cursor.fetchone()['count']
            student['created_at'] = student['created_at'].strftime('%Y-%m-%d')
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'students': students,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page
        }), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error fetching students'}), 500

@app.route('/api/admin/students/<int:student_id>', methods=['GET'])
@admin_login_required
def admin_get_student_details(student_id):
    """Get detailed student information"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get student info
        cursor.execute("""
            SELECT id, name, email, department, semester, created_at 
            FROM students 
            WHERE id = %s
        """, (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get student notes
        cursor.execute("""
            SELECT id, subject, title, description, upload_date 
            FROM notes 
            WHERE student_id = %s 
            ORDER BY upload_date DESC
        """, (student_id,))
        notes = cursor.fetchall()
        
        for note in notes:
            note['upload_date'] = note['upload_date'].strftime('%Y-%m-%d')
        
        student['created_at'] = student['created_at'].strftime('%Y-%m-%d')
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'student': student,
            'notes': notes,
            'notes_count': len(notes)
        }), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error fetching student details'}), 500

@app.route('/api/admin/students/<int:student_id>', methods=['DELETE'])
@admin_login_required
def admin_delete_student(student_id):
    """Delete a student and all their notes"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get all notes for this student
        cursor.execute("SELECT file_name FROM notes WHERE student_id = %s", (student_id,))
        notes = cursor.fetchall()
        
        # Delete files
        for note in notes:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], note['file_name'])
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        
        # Delete notes from database
        cursor.execute("DELETE FROM notes WHERE student_id = %s", (student_id,))
        
        # Delete student
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'Student deleted successfully'}), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error deleting student'}), 500

@app.route('/api/admin/notes', methods=['GET'])
@admin_login_required
def admin_get_notes():
    """Get all notes with student information"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM notes")
        total = cursor.fetchone()['total']
        
        # Get paginated notes with student info
        query = """
            SELECT n.id, n.subject, n.title, n.description, n.upload_date,
                   s.name as student_name, s.email as student_email, s.id as student_id
            FROM notes n
            JOIN students s ON n.student_id = s.id
            ORDER BY n.upload_date DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        notes = cursor.fetchall()
        
        for note in notes:
            note['upload_date'] = note['upload_date'].strftime('%Y-%m-%d')
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'notes': notes,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page
        }), 200
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Error fetching notes'}), 500

if __name__ == '__main__':
    create_upload_folder()
    app.run(debug=True)
