# Notes Upload App - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### 1. Setup MySQL Database
```bash
mysql -u root -p < database.sql
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database (if needed)
Edit `app.py` line 23-28 and update:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',              # ← Your MySQL username
    'password': 'your_password',  # ← Your MySQL password
    'database': 'notes_app'
}
```

### 4. Run the Application
```bash
python app.py
```

### 5. Open in Browser
Visit: **http://localhost:5000**

---

## 📝 Default Login/Access

The application has **no authentication** by default. All users can:
- Upload notes
- View all notes
- Download notes
- Search notes
- Delete notes

---

## 🎯 First Steps

1. **Navigate to Upload Page**: Click "Upload Notes" in the menu
2. **Create a Test Note**:
   - Subject: "Mathematics"
   - Title: "Algebra Basics"
   - Description: "Introduction to algebra concepts"
   - File: Upload a PDF or text file
3. **Go to View Notes**: Click "View Notes" or the home link
4. **Try Searching**: Type "Mathematics" in the search bar
5. **Download**: Click the download button on any note
6. **Delete**: Click the delete button to remove a note

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | MySQL server not running. Start MySQL service |
| "1045 - Access denied" | Wrong MySQL password in app.py. Update line 27 |
| "Upload folder not found" | Run Flask app once (folder auto-creates) |
| "No such table" | Run `mysql -u root -p < database.sql` |
| File upload fails | Check file is PDF/TXT/DOC/DOCX and < 50MB |

---

## 📁 File Locations

- **Uploaded files**: `static/uploads/` (auto-created)
- **Database**: MySQL (configured in `app.py`)
- **Logs**: Flask console output

---

## 🔒 Default Security

- File types: PDF, TXT, DOC, DOCX only
- Max file size: 50MB
- File names are sanitized
- SQL injection protection enabled

---

## 🎨 Customization

- **Change colors**: Edit `static/css/style.css`
- **Add features**: Modify `app.py` routes and `templates/*.html`
- **Adjust file size limit**: Change `MAX_FILE_SIZE` in `app.py`

---

## 📚 Full Documentation

See **README.md** for complete documentation and advanced setup.

---

**Ready to start? Run `python app.py` now!** 🎉
