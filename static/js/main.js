// Main JavaScript for Puppy Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Set default dates in filter form if empty
    var startDateInput = document.getElementById('start_date');
    var endDateInput = document.getElementById('end_date');
    
    if (startDateInput && !startDateInput.value) {
        var defaultStartDate = new Date();
        defaultStartDate.setDate(defaultStartDate.getDate() - 7);
        startDateInput.value = formatDate(defaultStartDate);
    }
    
    if (endDateInput && !endDateInput.value) {
        var defaultEndDate = new Date();
        endDateInput.value = formatDate(defaultEndDate);
    }
});

// Helper function to format date as YYYY-MM-DD
function formatDate(date) {
    var year = date.getFullYear();
    var month = (date.getMonth() + 1).toString().padStart(2, '0');
    var day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Function to format date in local format like "Mon Apr 7 06:43:19 PM ACST 2025"
function formatLocalDateTime() {
    const now = new Date();
    const options = { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric', 
        hour: 'numeric', 
        minute: 'numeric', 
        second: 'numeric',
        hour12: true
    };
    return now.toLocaleString('en-US', options) + ' ACST';
}

// Function to get current local time formatted for datetime-local input
function getCurrentLocalTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Handle service worker registration for PWA support (future enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js').then(function(registration) {
            console.log('ServiceWorker registration successful');
        }).catch(function(err) {
            console.log('ServiceWorker registration failed: ', err);
        });
    });
}