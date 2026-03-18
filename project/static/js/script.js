const CONFIG = {
    API_BASE: '/api',
    TIMEOUT: 5000,
};

// ===== NOTIFICATION =====
function showNotification(msg, type = 'info') {
    alert(msg); // simple for stability
}

// ===== FETCH =====
async function fetchAPI(url, options = {}) {
    const res = await fetch(url, options);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Error');
    return data;
}

// ===== LOGIN =====
function initializeLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            await fetchAPI('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email, password })
            });

            localStorage.setItem('studentName', email);

            window.location.href = '/dashboard';

        } catch (err) {
            showNotification(err.message, 'error');
        }
    });
}

// ===== LOAD NOTES =====
async function loadNotes() {
    const container = document.getElementById('notesGrid');
    if (!container) return;

    try {
        const notes = await fetchAPI('/api/notes');

        container.innerHTML = notes.map(n => `
            <div>
                <h3>${n.title}</h3>
                <p>${n.description || ''}</p>
                <a href="/api/download/${n.id}">Download</a>
                <button onclick="deleteNote(${n.id})">Delete</button>
            </div>
        `).join('');

    } catch (err) {
        container.innerHTML = "Failed to load notes";
    }
}

// ===== UPLOAD =====
function initializeUploadForm() {
    const form = document.getElementById('uploadForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        try {
            await fetchAPI('/api/upload', {
                method: 'POST',
                body: formData
            });

            showNotification("Uploaded successfully");
            window.location.href = "/notes";

        } catch (err) {
            showNotification(err.message);
        }
    });
}

// ===== DELETE =====
async function deleteNote(id) {
    if (!confirm("Delete note?")) return;

    try {
        await fetchAPI(`/api/delete/${id}`, {
            method: 'DELETE'
        });

        loadNotes();

    } catch (err) {
        showNotification(err.message);
    }
}

// ===== LOGOUT =====
function logout() {
    localStorage.clear();
    window.location.href = "/logout";
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    initializeLoginForm();
    initializeUploadForm();
    loadNotes();
});

// ===== GLOBAL =====
window.deleteNote = deleteNote;
window.logout = logout;
