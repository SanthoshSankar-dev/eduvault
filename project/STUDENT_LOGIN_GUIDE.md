# EduVault Student Login System Guide

## Overview
EduVault now includes a complete student authentication system with login and registration functionality. Each student must create an account to upload and manage their study notes.

## Features

### 1. Student Registration
Students can create a new account with the following information:
- **Full Name**: Student's complete name
- **Email**: Unique email address for login
- **Department**: Computer Science, Engineering, Science, Arts, Commerce, Medical, or Law
- **Semester**: 1st through 8th Semester
- **Password**: Secure password (minimum 6 characters)

### 2. Student Login
After registration, students can log in with:
- **Email Address**: Their registered email
- **Password**: Their secure password

### 3. Session Management
- Sessions are stored in Flask's secure session management
- Students are automatically logged out if they close the browser or click the logout button
- Protected routes require authentication (dashboard, upload, view notes)

### 4. User Profile
Each student's notes are isolated and only visible to them:
- Can only view/edit/delete their own notes
- Dashboard shows personalized welcome message
- Navigation bar displays student name and avatar with initials
- Logout button in the profile dropdown

## Database Schema

### Students Table
```sql
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL (hashed with werkzeug),
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    semester VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Notes Table (Updated)
```sql
CREATE TABLE notes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL (refers to students.id),
    subject VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_name VARCHAR(255) NOT NULL,
    upload_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -- Foreign key ensures notes are tied to students
);
```

## API Endpoints

### Authentication APIs
- **POST /api/login**
  - Request: `{ email, password }`
  - Response: `{ message, student_id, name, email }`
  
- **POST /api/register**
  - Request: `{ name, email, password, department, semester }`
  - Response: `{ message }`
  
- **POST /api/logout**
  - Clears session and logs out user
  
- **GET /api/current-student**
  - Returns: `{ student_id, email, name }`

### Note APIs (All require authentication)
- **GET /api/notes?search=query**
  - Returns: All notes for current student (filtered if search query provided)
  
- **POST /api/upload**
  - Uploads note and associates with current student
  
- **DELETE /api/delete/<note_id>**
  - Deletes note (only if owned by current student)

## Security Features

### Password Security
- Passwords are hashed using werkzeug's `generate_password_hash()`
- Uses PBKDF2 with SHA256 algorithm
- Passwords are never stored in plain text
- Minimum 6 character password requirement

### Access Control
- Only authenticated students can access dashboard, upload, and view pages
- Students can only delete their own notes (owner verification in backend)
- Search results only show current student's notes
- Login decorator (`@login_required`) protects routes

### Session Security
- Flask's secret key used for session signing
- Session data includes student_id, email, and name
- Sessions are tied to user browsers

## Setup Instructions

### 1. Initialize Database
Run the provided `database.sql` file in MySQL to create the students and notes tables:
```sql
mysql -u root -p < database.sql
```

### 2. Update MySQL Configuration
In `app.py`, update the database connection settings:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Your MySQL password
    'database': 'notes_app'
}
```

### 3. Install Dependencies
Ensure Flask and mysql-connector are installed:
```bash
pip install flask mysql-connector-python werkzeug
```

### 4. Start the Application
```bash
python app.py
```

### 5. Access the Application
1. Visit `http://localhost:5000/login`
2. Click "Create one here" to register as a new student
3. Enter your details and create an account
4. Log in with your email and password
5. Start uploading and managing your notes!

## Testing

### Create a Test Account
1. Go to login page: `http://localhost:5000/login`
2. Click on "Create one here"
3. Fill in test details:
   - Name: Test Student
   - Email: test@college.edu
   - Password: password123
   - Department: Computer Science
   - Semester: 3rd Semester
4. Click "Create Account"
5. Log in with test@college.edu and password123

### Test Study Flow
1. **Register**: Create multiple student accounts
2. **Upload**: Each student uploads sample notes
3. **View**: Log in as different students and verify they only see their own notes
4. **Download**: Test downloading notes
5. **Delete**: Test deleting own notes
6. **Logout**: Test logout functionality

## Troubleshooting

### "Invalid email or password"
- Verify email is correct
- Check password (case-sensitive)
- Ensure you've registered before attempting login

### "Email already registered"
- Use a different email address
- Or reset your password through email (if email feature is added)

### "Not logged in" error
- Your session may have expired
- Log back in at the login page
- Clear browser cookies if needed

### Database connection failed
- Check MySQL is running
- Verify credentials in app.py db_config
- Ensure database and tables are created

## Future Enhancements

- Email verification on registration
- Password reset functionality
- Account profile editing
- Social login (Google, GitHub)
- Two-factor authentication
- Student role-based access control (admin, teacher, student)
- Course enrollment system

## Files Modified

- **app.py**: Added login/registration routes and authentication logic
- **database.sql**: Added students table with proper schema
- **templates/login.html**: Updated with registration form
- **templates/dashboard.html**: Added student info display and logout
- **templates/upload_notes.html**: Added logout functionality
- **templates/view_notes.html**: Added logout functionality
- **static/css/style.css**: Added dropdown menu styling for logout
