# Notes Upload Web Application

A simple web application where students can upload study notes and other students can view and download them. The system allows searching notes by subject.

## Features

✅ **Upload Notes** - Create a form where users can upload notes with subject, title, description, and files (PDF, TXT, DOC, DOCX)

✅ **View Notes List** - Display all uploaded notes in a table or card layout with subject, title, description, upload date, and download button

✅ **Download Notes** - Each note has a download button that downloads the uploaded file

✅ **Search Notes** - Search bar where users can search notes by subject name

✅ **Responsive Design** - Works on desktop, tablet, and mobile devices

✅ **Delete Notes** - Users can delete notes they no longer need

## Technology Stack

### Frontend
- **HTML** - Structure
- **CSS** - Styling with responsive design
- **JavaScript** - Search, form validation, and interactivity

### Backend
- **Python** - Programming language
- **Flask** - Web framework for handling routes and file uploads
- **MySQL** - Database for storing note information

## Project Structure

```
project/
├── static/
│   ├── css/
│   │   └── style.css          # CSS styling
│   ├── uploads/               # Uploaded files directory (auto-created)
│   └── js/
│       └── script.js          # JavaScript utilities
├── templates/
│   ├── upload.html            # Upload form page
│   └── notes.html             # Notes listing page
├── app.py                     # Flask application
├── database.sql               # MySQL database schema
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- MySQL Server
- pip (Python package manager)

### Step 1: Clone or Download the Project

Download or clone the project to your local machine:
```bash
cd project
```

### Step 2: Create MySQL Database

1. Open MySQL command line or MySQL Workbench
2. Run the `database.sql` file to create the database and table:

```bash
mysql -u root -p < database.sql
```

Or manually run these commands in MySQL:
```sql
CREATE DATABASE IF NOT EXISTS notes_app;
USE notes_app;

CREATE TABLE IF NOT EXISTS notes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_name VARCHAR(255) NOT NULL,
    upload_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subject ON notes(subject);
CREATE INDEX idx_title ON notes(title);
```

### Step 3: Install Python Dependencies

Create a virtual environment (recommended):
```bash
python -m venv venv
```

Activate the virtual environment:
- **On Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

Install required packages:
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database Connection

Edit `app.py` and update the database configuration if needed:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',           # Your MySQL username
    'password': '',           # Your MySQL password
    'database': 'notes_app'
}
```

### Step 5: Run the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Usage

### Upload Notes
1. Navigate to the "Upload Notes" page
2. Fill in the following fields:
   - **Subject Name**: The subject of the notes (e.g., Mathematics, Physics)
   - **Note Title**: Title of the notes
   - **Description**: Brief description of the content (optional)
   - **File**: Upload a PDF, TXT, DOC, or DOCX file
3. Click "Upload Notes" button

### View Notes
1. Go to the "View Notes" page (index page)
2. All uploaded notes are displayed in a table (desktop) or cards (mobile)
3. Each note shows:
   - Subject name
   - Title
   - Description
   - Upload date
   - Download button
   - Delete button

### Search Notes
1. Enter a subject name or note title in the search bar
2. Click "Search" or press Enter
3. Results will be filtered based on your search query
4. Click "Clear" to reset the search and see all notes

### Download Notes
1. Click the "📥 Download" button next to any note
2. The file will be downloaded to your default downloads folder

### Delete Notes
1. Click the "🗑️ Delete" button next to any note
2. Confirm the deletion when prompted
3. The note will be permanently removed from the system

## Database Schema

### notes Table

| Field | Type | Description |
|-------|------|-------------|
| id | INT | Primary key, auto-increment |
| subject | VARCHAR(100) | Subject name |
| title | VARCHAR(200) | Note title |
| description | TEXT | Note description |
| file_name | VARCHAR(255) | Uploaded file name |
| upload_date | DATE | Date of upload |
| created_at | TIMESTAMP | Creation timestamp |

## API Endpoints

### GET /
- Renders the notes listing page

### GET /upload
- Renders the upload form page

### GET /api/notes
- Returns all notes as JSON
- Query parameter: `search` (optional) - Search term for subject or title

### POST /api/upload
- Upload a new note
- Form data: subject, title, description, file
- Returns: JSON response with success message or error

### GET /api/download/<note_id>
- Download a specific note file
- Parameter: note_id (integer)
- Returns: File download

### DELETE /api/delete/<note_id>
- Delete a specific note
- Parameter: note_id (integer)
- Returns: JSON response with success message or error

## Features & Highlights

### Security
- Files are validated on both client and server side
- File types are restricted to safe formats
- File size limit of 50MB
- SQL injection protection with parameterized queries

### Performance
- Database indexes on frequently searched columns
- Responsive design for all devices
- Optimized CSS and JavaScript

### User Experience
- Clean and intuitive interface
- Form validation with helpful error messages
- Loading indicators for file uploads
- Success/error notification system
- Mobile-friendly responsive design

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Android Chrome)

## Customization

### Change File Upload Limit
In `app.py`, modify the `MAX_FILE_SIZE` constant:
```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB (change this value)
```

### Allowed File Types
In `app.py`, modify the `ALLOWED_EXTENSIONS` set:
```python
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}  # Add or remove extensions
```

### Styling
All CSS styles are in `static/css/style.css`. Customize colors, fonts, and layouts as needed.

## Troubleshooting

### Database Connection Error
- Ensure MySQL Server is running
- Check database credentials in `app.py`
- Verify database and table exist

### File Upload Error
- Check that the `static/uploads` directory exists and is writable
- Ensure file size is under 50MB
- Verify file type is allowed (PDF, TXT, DOC, DOCX)

### Notes Not Displaying
- Check browser console for JavaScript errors
- Ensure database connection is working
- Verify there are uploaded notes in the database

### Permission Error
- Ensure the Flask process has write permissions to the `static/uploads` directory
- On Linux/Mac, run: `chmod 755 static/uploads`

## Deployment

### Moving to Production

1. Set Flask's `debug` mode to `False` in `app.py`:
   ```python
   if __name__ == '__main__':
       app.run(debug=False)
   ```

2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

3. Set up a reverse proxy (Nginx/Apache) in front of the Flask app

4. Use environment variables for sensitive data:
   ```python
   import os
   db_config = {
       'host': os.getenv('DB_HOST', 'localhost'),
       'user': os.getenv('DB_USER', 'root'),
       'password': os.getenv('DB_PASSWORD', ''),
       'database': os.getenv('DB_NAME', 'notes_app')
   }
   ```

## Future Enhancements

- User authentication and registration
- User profiles and favorites
- Rating and review system
- Share notes with specific users
- Advanced search filters
- Note categories
- Full-text search
- Backup and restore functionality
- Email notifications
- API rate limiting

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please create an issue or contact the development team.

## Author

Created as a simple notes upload application for students.

---

**Happy learning! 📚**
