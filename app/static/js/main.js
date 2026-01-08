document.addEventListener('DOMContentLoaded', () => {


    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Register Service Worker
let deferredPrompt;

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('Service Worker registered', reg))
            .catch(err => console.log('Service Worker registration failed', err));
    });
}

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;
    // Update UI notify the user they can install the PWA
    const installBtn = document.getElementById('installBtn');
    if (installBtn) installBtn.style.display = 'flex';
});

document.addEventListener('click', (e) => {
    if (e.target.id === 'installBtn' || e.target.closest('#installBtn')) {
        const installBtn = document.getElementById('installBtn');
        if (installBtn) installBtn.style.display = 'none';
        // Show the prompt
        if (deferredPrompt) {
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the A2HS prompt');
                } else {
                    console.log('User dismissed the A2HS prompt');
                }
                deferredPrompt = null;
            });
        }
    }
});

window.addEventListener('appinstalled', (evt) => {
    console.log('OmNi installed');
    const installBtn = document.getElementById('installBtn');
    if (installBtn) installBtn.style.display = 'none';
});

// ========================================
// Performance Mode Toggle
// ========================================
function initPerfMode() {
    const saved = localStorage.getItem('perfMode');
    if (saved === 'true') {
        document.body.classList.add('perf-mode');
    }
    updatePerfToggleUI();
}

function togglePerfMode() {
    document.body.classList.toggle('perf-mode');
    const isPerf = document.body.classList.contains('perf-mode');
    localStorage.setItem('perfMode', isPerf);
    updatePerfToggleUI();
}

function updatePerfToggleUI() {
    const btn = document.getElementById('perfToggle');
    if (!btn) return;
    const isPerf = document.body.classList.contains('perf-mode');
    btn.innerHTML = isPerf ? '✨ Quality' : '⚡ Perf';
    btn.title = isPerf ? 'Switch to Quality Mode (blur effects)' : 'Switch to Performance Mode (faster scrolling)';
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initPerfMode);

// ========================================
// Easter Egg: Matrix Theme
// Type "matrix" anywhere to activate!
// ========================================
let matrixBuffer = '';
const MATRIX_CODE = 'matrix';

document.addEventListener('keypress', (e) => {
    // Don't trigger in input fields
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    matrixBuffer += e.key.toLowerCase();

    // Keep only last 6 characters
    if (matrixBuffer.length > MATRIX_CODE.length) {
        matrixBuffer = matrixBuffer.slice(-MATRIX_CODE.length);
    }

    // Check for match
    if (matrixBuffer === MATRIX_CODE) {
        activateMatrix();
        matrixBuffer = '';
    }
});

function activateMatrix() {
    const body = document.body;
    const isMatrix = body.classList.contains('theme-matrix');

    // Flash effect
    body.classList.add('matrix-activate');
    setTimeout(() => body.classList.remove('matrix-activate'), 500);

    // Toggle theme
    body.classList.toggle('theme-matrix');

    // Persist preference
    localStorage.setItem('themeMatrix', !isMatrix);

    // Console easter egg
    console.log(isMatrix ? '🔵 Back to reality...' : '🟢 Welcome to the Matrix, Neo.');
}

// Restore Matrix theme on load
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('themeMatrix') === 'true') {
        document.body.classList.add('theme-matrix');
    }
});
