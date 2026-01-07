// Configuration
const API_HOST = 'https://judge.iut-aiagent.ir';
const API_BASE = `${API_HOST}/api`;

// Utility functions
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = 'login.html';
            return;
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

function checkAuth() {
    if (!localStorage.getItem('access_token')) {
        window.location.href = 'login.html';
    }
}

function formatTime(date) {
    return new Date(date).toLocaleString();
}