/**
 * EduVault - College Notes Portal
 * Modern JavaScript Framework
 */

// ===== CONFIGURATION =====

const CONFIG = {
    API_BASE: '/api',
    TIMEOUT: 5000,
};

// ===== UTILITIES =====

function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `<span>${message}</span>`;
    notification.style.position = 'fixed';
    notification.style.bottom = '2rem';
    notification.style.right = '2rem';
    notification.style.zIndex = '1000';

    document.body.appendChild(notification);

    if (duration > 0) {
        setTimeout(() => notification.remove(), duration);
    }

    return notification;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function truncateText(text, length = 100) {
    return text && text.length > length ? text.substring(0, length) + '...' : text;
}

function escapeHtml(unsafe) {
    return unsafe
        ? unsafe.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
        : '';
}

// ===== FETCH WITH TIMEOUT =====

async function fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);

    const response = await fetch(url, {
        ...options,
        signal: controller.signal
    });

    clearTimeout(id);
    return response;
}

// ===== API FUNCTIONS =====

async function fetchNotes() {
    const res = await fetchWithTimeout(`${CONFIG.API_BASE}/notes`);
    return await res.json();
}

async function uploadNote(formData) {
    const res = await fetchWithTimeout(`${CONFIG.API_BASE}/upload`, {
        method: 'POST',
        body: formData
    });
    return await res.json();
}

async function deleteNote(id) {
    const res = await fetchWithTimeout(`${CONFIG.API_BASE}/delete/${id}`, {
        method: 'DELETE'
    });
    return await res.json();
}

// ===== DISPLAY =====

function displayNotes(notes) {
    const container = document.getElementById('notesGrid');
    if (!container) return;

    container.innerHTML = notes.map(note => `
        <div class="note-card">
            <h3>${escapeHtml(note.title)}</h3>
            <p>${escapeHtml(note.description || '')}</p>
            <button onclick="handleDeleteNote(${note.id})">Delete</button>
        </div>
    `).join('');
}

// ===== DELETE =====

async function handleDeleteNote(id) {
    if (!confirm('Delete note?')) return;

    await deleteNote(id);
    location.reload();
}

// ===== LOGIN FIXED 🔥 =====

function initializeLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();

        if (!email || !password) {
            showNotification('Fill all fields', 'error');
            return;
        }

        const btn = form.querySelector('button');
        btn.disabled = true;
        btn.innerText = 'Loading...';

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (!res.ok) throw new Error(data.error);

            localStorage.setItem('studentName', email.split('@')[0]);

            showNotification('Login success', 'success');

            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 800);

        } catch (err) {
            showNotification('Login failed', 'error');
        }

        btn.disabled = false;
        btn.innerText = 'Login';
    });
}

// ===== INIT =====

document.addEventListener('DOMContentLoaded', () => {
    initializeLoginForm();
});
