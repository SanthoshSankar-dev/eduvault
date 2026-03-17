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

/**
 * Show a toast notification
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `<span>${message}</span>`;
    notification.style.position = 'fixed';
    notification.style.bottom = '2rem';
    notification.style.right = '2rem';
    notification.style.zIndex = '1000';
    notification.style.maxWidth = '400px';
    notification.style.margin = '0';

    document.body.appendChild(notification);

    if (duration > 0) {
        setTimeout(() => {
            notification.remove();
        }, duration);
    }

    return notification;
}

/**
 * Format date to readable format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Truncate text to specified length
 */
function truncateText(text, length = 100) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
}

/**
 * Escape HTML special characters
 */
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Debounce function
 */
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Fetch with timeout
 */
async function fetchWithTimeout(url, options = {}) {
    const timeout = options.timeout || CONFIG.TIMEOUT;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        throw error;
    }
}

// ===== API FUNCTIONS =====

/**
 * Fetch notes from API
 */
async function fetchNotes(searchQuery = '') {
    try {
        const url = searchQuery 
            ? `${CONFIG.API_BASE}/notes?search=${encodeURIComponent(searchQuery)}`
            : `${CONFIG.API_BASE}/notes`;

        const response = await fetchWithTimeout(url);
        
        if (!response.ok) {
            throw new Error('Failed to fetch notes');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching notes:', error);
        throw error;
    }
}

/**
 * Upload a note
 */
async function uploadNote(formData) {
    try {
        const response = await fetchWithTimeout(`${CONFIG.API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Error uploading note:', error);
        throw error;
    }
}

/**
 * Delete a note
 */
async function deleteNote(noteId) {
    try {
        const response = await fetchWithTimeout(`${CONFIG.API_BASE}/delete/${noteId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Delete failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Error deleting note:', error);
        throw error;
    }
}

// ===== SEARCH & FILTER =====

/**
 * Filter notes in memory
 */
function filterNotes(notes, searchQuery) {
    if (!searchQuery) return notes;

    const query = searchQuery.toLowerCase();
    return notes.filter(note => 
        note.subject.toLowerCase().includes(query) ||
        note.title.toLowerCase().includes(query) ||
        (note.description && note.description.toLowerCase().includes(query))
    );
}

/**
 * Initialize search functionality
 */
function initializeSearch(notesContainer) {
    const searchInput = document.getElementById('noteSearch');
    const clearBtn = document.getElementById('clearSearch');
    const searchBtn = document.getElementById('searchBtn');

    if (!searchInput) return;

    let allNotes = [];

    // Load all notes on init
    loadAllNotes();

    async function loadAllNotes() {
        try {
            allNotes = await fetchNotes();
            displayNotes(allNotes);
        } catch (error) {
            showNotification('Failed to load notes', 'error');
        }
    }

    // Search handler
    const handleSearch = debounce(async () => {
        const query = searchInput.value.trim();
        
        if (query) {
            try {
                const results = await fetchNotes(query);
                displayNotes(results);
                if (clearBtn) clearBtn.style.display = 'inline-block';
            } catch (error) {
                showNotification('Search failed', 'error');
            }
        } else {
            displayNotes(allNotes);
            if (clearBtn) clearBtn.style.display = 'none';
        }
    }, 300);

    searchInput.addEventListener('input', handleSearch);
    
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
    }

    // Clear search
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            displayNotes(allNotes);
            clearBtn.style.display = 'none';
        });
    }

    // Search on Enter key
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
}

// ===== DISPLAY NOTES =====

/**
 * Display notes in cards
 */
function displayNotes(notes) {
    const container = document.getElementById('notesGrid');
    const stats = document.getElementById('notesStats');

    if (!container) return;

    if (notes.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-icon">📚</div>
                <h3>No Notes Found</h3>
                <p>No notes match your search criteria. Try uploading some notes or adjusting your search.</p>
            </div>
        `;
        if (stats) {
            stats.innerHTML = '<div class="stat"><span class="stat-number">0</span> notes found</div>';
        }
        return;
    }

    container.innerHTML = notes.map(note => `
        <div class="note-card">
            <div class="note-card-header">
                <div class="note-subject">${escapeHtml(note.subject)}</div>
                <div class="note-title">${escapeHtml(note.title)}</div>
            </div>
            <div class="note-card-body">
                <p class="note-description">${escapeHtml(truncateText(note.description || 'No description', 150))}</p>
                <div class="note-meta">
                    <div class="note-date">
                        <span>📅</span>
                        <span>${formatDate(note.upload_date)}</span>
                    </div>
                </div>
            </div>
            <div class="note-card-footer">
                <a href="/api/download/${note.id}" class="btn btn-sm btn-primary">
                    📥 Download
                </a>
                <button class="btn btn-sm btn-danger" onclick="handleDeleteNote(${note.id})">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');

    if (stats) {
        stats.innerHTML = `<div class="stat"><span class="stat-number">${notes.length}</span> note${notes.length !== 1 ? 's' : ''} found</div>`;
    }
}

// ===== FORM HANDLERS =====

/**
 * Initialize upload form
 */
function initializeUploadForm() {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('noteFile');
    const fileLabel = document.querySelector('.file-input-text');

    if (!form) return;

    // File input change handler
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const fileName = e.target.files[0]?.name || 'Choose file';
            if (fileLabel) {
                fileLabel.textContent = fileName;
            }
        });
    }

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validate form
        if (!validateForm(form)) {
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loader" style="width: 20px; height: 20px; border-width: 2px;"></span>';

        try {
            const formData = new FormData(form);
            await uploadNote(formData);
            
            showNotification('Note uploaded successfully!', 'success');
            form.reset();
            if (fileLabel) fileLabel.textContent = 'Choose file';
            
            // Redirect after delay
            setTimeout(() => {
                window.location.href = '/view-notes';
            }, 1500);
        } catch (error) {
            showNotification(error.message || 'Upload failed', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

/**
 * Validate form fields
 */
function validateForm(form) {
    const fields = form.querySelectorAll('[required]');
    let isValid = true;

    fields.forEach(field => {
        const value = field.value.trim();
        
        if (!value) {
            field.style.borderColor = '#EF4444';
            isValid = false;
        } else {
            field.style.borderColor = '';
        }
    });

    return isValid;
}

/**
 * Handle note deletion
 */
async function handleDeleteNote(noteId) {
    if (!confirm('Are you sure you want to delete this note? This action cannot be undone.')) {
        return;
    }

    try {
        await deleteNote(noteId);
        showNotification('Note deleted successfully', 'success');
        
        // Reload notes
        setTimeout(() => {
            location.reload();
        }, 1000);
    } catch (error) {
        showNotification(error.message || 'Failed to delete note', 'error');
    }
}

/**
 * Initialize login form
 */
function initializeLoginForm() {
    const form = document.getElementById('loginForm');
    
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();

        // Basic validation
        if (!email || !password) {
            showNotification('Please fill in all fields', 'error');
            return;
        }

        // Simple email validation
        if (!email.includes('@')) {
            showNotification('Please enter a valid email', 'error');
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loader" style="width: 20px; height: 20px; border-width: 2px;"></span>';

        // Simulate login (in production, this would call a real API)
        setTimeout(() => {
            localStorage.setItem('studentEmail', email);
            localStorage.setItem('studentName', email.split('@')[0]);
            showNotification('Login successful! Redirecting...', 'success');
            
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 800);
        }, 500);
    });
}

/**
 * Update navbar with student info
 */
function updateNavbarWithStudentInfo() {
    const studentName = localStorage.getItem('studentName') || 'Student';
    const profileElement = document.getElementById('studentProfile');
    
    if (profileElement) {
        const initials = studentName
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
        
        profileElement.textContent = initials;
    }

    const nameElement = document.getElementById('studentName');
    if (nameElement) {
        nameElement.textContent = studentName;
    }
}

// ===== SIDEBAR/MENU =====

/**
 * Initialize mobile menu toggle
 */
function initializeMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const navbar = document.querySelector('.navbar-menu');

    if (!menuToggle || !navbar) return;

    menuToggle.addEventListener('click', () => {
        navbar.classList.toggle('active');
    });

    // Close menu when link is clicked
    document.querySelectorAll('.navbar-menu a').forEach(link => {
        link.addEventListener('click', () => {
            navbar.classList.remove('active');
        });
    });
}

// ===== INITIALIZATION =====

/**
 * Initialize all features
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('EduVault initialized');
    
    // Update navbar with student info
    updateNavbarWithStudentInfo();
    
    // Initialize mobile menu
    initializeMobileMenu();
    
    // Initialize upload form
    initializeUploadForm();
    
    // Initialize login form
    initializeLoginForm();
    
    // Initialize search
    initializeSearch();
    
    // Set active navbar link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-menu a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// ===== EXPORT FUNCTIONS =====

window.showNotification = showNotification;
window.formatDate = formatDate;
window.truncateText = truncateText;
window.escapeHtml = escapeHtml;
window.handleDeleteNote = handleDeleteNote;
window.displayNotes = displayNotes;
window.fetchNotes = fetchNotes;

