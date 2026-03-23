/**
 * Utility Functions
 */

// ==================== Storage Helpers ====================

/**
 * Save data to localStorage
 * @param {string} key - Key to save under
 * @param {*} value - Value to save
 */
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.error('Storage error:', e);
    }
}

/**
 * Get data from localStorage
 * @param {string} key - Key to retrieve
 * @returns {*} Stored value or null
 */
function getFromStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (e) {
        console.error('Storage error:', e);
        return null;
    }
}

/**
 * Remove data from localStorage
 * @param {string} key - Key to remove
 */
function removeFromStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (e) {
        console.error('Storage error:', e);
    }
}

// ==================== Array Helpers ====================

/**
 * Check if value exists in array
 * @param {Array} array - Array to check
 * @param {*} value - Value to find
 * @returns {boolean} True if found
 */
function arrayIncludes(array, value) {
    return array.includes(value);
}

/**
 * Remove duplicates from array
 * @param {Array} array - Array to deduplicate
 * @returns {Array} New array without duplicates
 */
function uniqueArray(array) {
    return [...new Set(array)];
}

/**
 * Group array items by property
 * @param {Array} array - Array of objects
 * @param {string} property - Property to group by
 * @returns {Object} Grouped object
 */
function groupByProperty(array, property) {
    return array.reduce((result, item) => {
        const key = item[property];
        if (!result[key]) {
            result[key] = [];
        }
        result[key].push(item);
        return result;
    }, {});
}

// ==================== String Helpers ====================

/**
 * Capitalize first letter
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncate string
 * @param {string} str - String to truncate
 * @param {number} length - Max length
 * @returns {string} Truncated string
 */
function truncate(str, length = 100) {
    return str.length > length ? str.substring(0, length) + '...' : str;
}

/**
 * Convert string to URL slug
 * @param {string} str - String to convert
 * @returns {string} URL-safe slug
 */
function toSlug(str) {
    return str.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
}

// ==================== Number Helpers ====================

/**
 * Round number to decimal places
 * @param {number} num - Number to round
 * @param {number} decimals - Decimal places
 * @returns {number} Rounded number
 */
function roundNumber(num, decimals = 2) {
    return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
}

/**
 * Format number as currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency symbol
 * @returns {string} Formatted currency
 */
function formatAmount(amount, currency = '₹') {
    return currency + roundNumber(amount, 2).toFixed(2);
}

/**
 * Get percentage
 * @param {number} part - Part value
 * @param {number} whole - Whole value
 * @returns {number} Percentage
 */
function getPercentage(part, whole) {
    return roundNumber((part / whole) * 100, 2);
}

// ==================== Date Helpers ====================

/**
 * Get days difference between two dates
 * @param {Date} date1 - First date
 * @param {Date} date2 - Second date
 * @returns {number} Difference in days
 */
function daysBetween(date1, date2) {
    const oneDay = 24 * 60 * 60 * 1000;
    return Math.round(Math.abs((date1 - date2) / oneDay));
}

/**
 * Check if date is today
 * @param {Date} date - Date to check
 * @returns {boolean} True if today
 */
function isToday(date) {
    const today = new Date();
    return date.getDate() === today.getDate() &&
        date.getMonth() === today.getMonth() &&
        date.getFullYear() === today.getFullYear();
}

/**
 * Get relative time string
 * @param {Date|string} date - Date to convert
 * @returns {string} Relative time (e.g., "2 hours ago")
 */
function getRelativeTime(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (days < 30) return `${days} day${days > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
}

// ==================== Object Helpers ====================

/**
 * Deep copy object
 * @param {Object} obj - Object to copy
 * @returns {Object} Deep copy
 */
function deepCopy(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Merge objects
 * @param {Object} target - Target object
 * @param {Object} source - Source object
 * @returns {Object} Merged object
 */
function mergeObjects(target, source) {
    return { ...target, ...source };
}

/**
 * Get nested property value
 * @param {Object} obj - Object to search
 * @param {string} path - Property path (e.g., "user.name")
 * @returns {*} Property value
 */
function getNestedProperty(obj, path) {
    return path.split('.').reduce((current, prop) => current?.[prop], obj);
}

// ==================== URL Helpers ====================

/**
 * Get URL query parameter
 * @param {string} param - Parameter name
 * @returns {string|null} Parameter value or null
 */
function getQueryParam(param) {
    const params = new URLSearchParams(window.location.search);
    return params.get(param);
}

/**
 * Build query string
 * @param {Object} params - Parameters object
 * @returns {string} Query string
 */
function buildQueryString(params) {
    return Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
}

// ==================== Element Helpers ====================

/**
 * Scroll to element
 * @param {HTMLElement} element - Element to scroll to
 */
function scrollToElement(element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Check if element is in viewport
 * @param {HTMLElement} element - Element to check
 * @returns {boolean} True if visible
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Wait for element to exist
 * @param {string} selector - CSS selector
 * @returns {Promise} Resolves when element found
 */
function waitForElement(selector) {
    return new Promise(resolve => {
        const element = document.querySelector(selector);
        if (element) {
            resolve(element);
            return;
        }
        
        const observer = new MutationObserver(() => {
            const element = document.querySelector(selector);
            if (element) {
                observer.disconnect();
                resolve(element);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}

// ==================== Debounce & Throttle ====================

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, delay = 300) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

/**
 * Throttle function
 * @param {Function} func - Function to throttle
 * @param {number} limit - Limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ==================== Error Handling ====================

/**
 * Handle error gracefully
 * @param {Error} error - Error object
 * @param {string} context - Context description
 */
function handleError(error, context = 'An error occurred') {
    console.error(`${context}:`, error);
    showNotification(`${context}: ${error.message}`, 'danger');
}

/**
 * Try-catch wrapper
 * @param {Function} func - Function to execute
 * @returns {Promise} Result or error
 */
async function tryCatch(func) {
    try {
        return await func();
    } catch (error) {
        handleError(error);
        throw error;
    }
}

// ==================== Export ====================

window.saveToStorage = saveToStorage;
window.getFromStorage = getFromStorage;
window.roundNumber = roundNumber;
window.formatAmount = formatAmount;
window.capitalize = capitalize;
window.truncate = truncate;
window.debounce = debounce;
window.throttle = throttle;
window.getRelativeTime = getRelativeTime;
window.deepCopy = deepCopy;