/**
 * AgriHaul Main JavaScript
 * 
 * Common functions used across all pages
 */

// ==================== Utility Functions ====================

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in milliseconds (default 3000)
 */
function showNotification(message, type = 'info', duration = 3000) {
    const alertClass = `alert alert-${type}`;
    const alertHTML = `
        <div class="${alertClass}">
            ${message}
            <button class="alert-close" onclick="this.parentElement.style.display='none';">&times;</button>
        </div>
    `;
    
    const container = document.querySelector('.alerts-container');
    if (!container) return;
    
    const div = document.createElement('div');
    div.innerHTML = alertHTML;
    container.appendChild(div.firstElementChild);
    
    if (duration > 0) {
        setTimeout(() => {
            const alert = container.lastElementChild;
            if (alert) alert.remove();
        }, duration);
    }
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}

/**
 * Format date
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Validate email
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number (Indian format)
 * @param {string} phone - Phone number to validate
 * @returns {boolean} True if valid 10-digit number
 */
function isValidPhone(phone) {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone);
}

/**
 * Confirm action with user
 * @param {string} message - Confirmation message
 * @returns {boolean} True if confirmed
 */
function confirmAction(message) {
    return confirm(message);
}

// ==================== Form Helpers ====================

/**
 * Get form data as object
 * @param {HTMLFormElement} form - Form element
 * @returns {Object} Form data as key-value pairs
 */
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });
    return data;
}

/**
 * Clear form inputs
 * @param {HTMLFormElement} form - Form element to clear
 */
function clearForm(form) {
    form.reset();
}

/**
 * Disable form inputs
 * @param {HTMLFormElement} form - Form to disable
 * @param {boolean} disabled - True to disable, false to enable
 */
function setFormDisabled(form, disabled = true) {
    const inputs = form.querySelectorAll('input, select, textarea, button');
    inputs.forEach(input => {
        input.disabled = disabled;
    });
}

/**
 * Show form errors
 * @param {Object} errors - Object with field names as keys and error messages as values
 */
function showFormErrors(errors) {
    Object.entries(errors).forEach(([field, message]) => {
        const input = document.querySelector(`[name="${field}"]`);
        if (input) {
            input.classList.add('error');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            input.parentElement.appendChild(errorDiv);
        }
    });
}

/**
 * Clear form errors
 */
function clearFormErrors() {
    document.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
    document.querySelectorAll('.error-message').forEach(el => el.remove());
}

// ==================== DOM Helpers ====================

/**
 * Toggle element visibility
 * @param {HTMLElement} element - Element to toggle
 */
function toggleElement(element) {
    if (element.style.display === 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

/**
 * Hide element
 * @param {HTMLElement} element - Element to hide
 */
function hideElement(element) {
    element.style.display = 'none';
}

/**
 * Show element
 * @param {HTMLElement} element - Element to show
 */
function showElement(element) {
    element.style.display = 'block';
}

/**
 * Add CSS class to element
 * @param {HTMLElement} element - Element to add class to
 * @param {string} className - Class name
 */
function addClass(element, className) {
    element.classList.add(className);
}

/**
 * Remove CSS class from element
 * @param {HTMLElement} element - Element to remove class from
 * @param {string} className - Class name
 */
function removeClass(element, className) {
    element.classList.remove(className);
}

// ==================== API Helpers ====================

/**
 * Make API request
 * @param {string} url - API endpoint URL
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {Object} data - Data to send (for POST requests)
 * @returns {Promise} Response from API
 */
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const json = await response.json();
        
        if (!response.ok) {
            throw new Error(json.error || `HTTP ${response.status}`);
        }
        
        return json;
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'danger');
        throw error;
    }
}

// ==================== Haversine Distance Calculation ====================

/**
 * Calculate distance between two coordinates using Haversine formula
 * @param {number} lat1 - Starting latitude
 * @param {number} lon1 - Starting longitude
 * @param {number} lat2 - Ending latitude
 * @param {number} lon2 - Ending longitude
 * @returns {number} Distance in kilometers
 */
function haversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

// ==================== Page Load Helpers ====================

/**
 * Initialize page
 * Called when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // Add smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// ==================== Debugging ====================

/**
 * Log debug information
 * @param {*} data - Data to log
 */
function debugLog(data) {
    if (window.DEBUG) {
        console.log('[DEBUG]', data);
    }
}

// ==================== Export for use ====================

window.showNotification = showNotification;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.haversineDistance = haversineDistance;
window.apiRequest = apiRequest;
window.confirmAction = confirmAction;
window.isValidEmail = isValidEmail;
window.isValidPhone = isValidPhone;