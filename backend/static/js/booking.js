/**
 * Booking Functions
 * 
 * Handle booking creation, updates, and related operations
 */

// ==================== Fare Calculation ====================

/**
 * Calculate fare based on distance and weight
 * @param {number} distance - Distance in km
 * @param {number} weight - Weight in kg
 * @returns {Object} Fare breakdown
 */
function calculateFare(distance, weight) {
    const baseFare = 100;
    const distanceRate = 10; // ₹ per km
    const weightRate = 0.50; // ₹ per kg
    
    const distanceCharge = distance * distanceRate;
    const weightCharge = weight * weightRate;
    const totalFare = baseFare + distanceCharge + weightCharge;
    
    return {
        baseFare: roundNumber(baseFare, 2),
        distanceCharge: roundNumber(distanceCharge, 2),
        weightCharge: roundNumber(weightCharge, 2),
        totalFare: roundNumber(totalFare, 2),
        distance: roundNumber(distance, 2),
        weight: weight
    };
}

/**
 * Update fare estimate display
 * @param {Object} fare - Fare object from calculateFare()
 */
function updateFareEstimate(fare) {
    const fareCard = document.getElementById('fare_estimate_card');
    if (!fareCard) return;
    
    document.getElementById('base_fare').textContent = '₹' + fare.baseFare;
    document.getElementById('distance_charge').textContent = '₹' + fare.distanceCharge;
    document.getElementById('weight_charge').textContent = '₹' + fare.weightCharge;
    document.getElementById('total_fare').textContent = '₹' + fare.totalFare;
    document.getElementById('distance_km_display').textContent = 'Distance: ' + fare.distance + ' km';
    
    fareCard.style.display = 'block';
}

// ==================== Available Drivers ====================

/**
 * Fetch and display available drivers
 * @param {number} pickupLat - Pickup latitude
 * @param {number} pickupLon - Pickup longitude
 * @param {number} weight - Weight in kg
 */
async function loadAvailableDrivers(pickupLat, pickupLon, weight) {
    try {
        const response = await apiRequest('/farmer/api/available-drivers', 'POST', {
            pickup_lat: pickupLat,
            pickup_lon: pickupLon,
            weight_kg: weight
        });
        
        if (response.success) {
            displayAvailableDrivers(response.drivers);
        } else {
            showNotification(response.error || 'Failed to load drivers', 'warning');
        }
    } catch (error) {
        console.error('Error loading drivers:', error);
    }
}

/**
 * Display drivers in list
 * @param {Array} drivers - Array of driver objects
 */
function displayAvailableDrivers(drivers) {
    const driversList = document.getElementById('drivers_list');
    const driversCard = document.getElementById('nearby_drivers_card');
    
    if (!driversList) return;
    
    if (drivers.length === 0) {
        driversList.innerHTML = '<p>No drivers available in your area</p>';
        driversCard.style.display = 'block';
        return;
    }
    
    let html = '<div class="drivers-grid">';
    
    drivers.forEach(driver => {
        html += `
            <div class="driver-card">
                <div class="driver-info">
                    <h4>${driver.name}</h4>
                    <p class="vehicle">${driver.vehicle}</p>
                </div>
                <div class="driver-distance">
                    <span class="distance-badge">${driver.distance_km} km</span>
                </div>
                <div class="driver-capacity">
                    <span class="capacity-badge">Cap: ${driver.capacity_kg} kg</span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    driversList.innerHTML = html;
    driversCard.style.display = 'block';
}

// ==================== Booking Status ====================

/**
 * Get status badge HTML
 * @param {string} status - Booking status
 * @returns {string} HTML for status badge
 */
function getStatusBadge(status) {
    return `<span class="status-badge status-${status.toLowerCase()}">${status}</span>`;
}

/**
 * Update booking status badge
 * @param {string} bookingId - Booking ID
 * @param {string} newStatus - New status
 */
function updateStatusBadge(bookingId, newStatus) {
    const badge = document.querySelector(`[data-booking-id="${bookingId}"] .status-badge`);
    if (badge) {
        badge.className = `status-badge status-${newStatus.toLowerCase()}`;
        badge.textContent = newStatus;
    }
}

// ==================== Accept Booking ====================

/**
 * Accept a booking as driver
 * @param {number} bookingId - Booking ID
 */
async function acceptBooking(bookingId) {
    if (!confirmAction('Are you sure you want to accept this booking?')) {
        return;
    }
    
    try {
        const response = await fetch(`/driver/accept/${bookingId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            showNotification('Booking accepted!', 'success');
            setTimeout(() => {
                window.location.href = `/driver/booking/${bookingId}`;
            }, 1000);
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to accept booking', 'danger');
        }
    } catch (error) {
        handleError(error, 'Failed to accept booking');
    }
}

/**
 * Complete a booking
 * @param {number} bookingId - Booking ID
 */
async function completeBooking(bookingId) {
    if (!confirmAction('Mark this booking as completed?')) {
        return;
    }
    
    try {
        const response = await fetch(`/driver/complete/${bookingId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Booking completed!', 'success');
            setTimeout(() => {
                window.location.href = '/driver/dashboard';
            }, 1000);
        } else {
            showNotification('Failed to complete booking', 'danger');
        }
    } catch (error) {
        handleError(error, 'Failed to complete booking');
    }
}

/**
 * Cancel a booking
 * @param {number} bookingId - Booking ID
 */
async function cancelBooking(bookingId) {
    if (!confirmAction('Are you sure you want to cancel this booking?')) {
        return;
    }
    
    try {
        const response = await fetch(`/farmer/booking/${bookingId}/cancel`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Booking cancelled', 'info');
            setTimeout(() => {
                window.location.href = '/farmer/bookings';
            }, 1000);
        } else {
            showNotification('Failed to cancel booking', 'danger');
        }
    } catch (error) {
        handleError(error, 'Failed to cancel booking');
    }
}

// ==================== Driver Status ====================

/**
 * Toggle driver availability
 */
async function toggleAvailability() {
    try {
        const response = await apiRequest('/driver/api/toggle-availability', 'POST');
        
        if (response.success) {
            showNotification(response.message, 'success');
            // Update status indicator
            const indicator = document.querySelector('.status-indicator');
            if (indicator) {
                indicator.className = `status-indicator ${response.is_available ? 'online' : 'offline'}`;
            }
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(response.error, 'danger');
        }
    } catch (error) {
        handleError(error, 'Failed to update availability');
    }
}

/**
 * Update driver location
 * @param {number} latitude - Current latitude
 * @param {number} longitude - Current longitude
 */
async function updateDriverLocation(latitude, longitude) {
    try {
        const response = await apiRequest('/driver/api/update-location', 'POST', {
            latitude: latitude,
            longitude: longitude
        });
        
        if (!response.success) {
            console.error('Failed to update location:', response.error);
        }
    } catch (error) {
        console.error('Location update error:', error);
    }
}

/**
 * Get driver's current location and update
 */
function enableLocationTracking() {
    if (!navigator.geolocation) {
        console.warn('Geolocation not supported');
        return;
    }
    
    const updateLocation = () => {
        navigator.geolocation.getCurrentPosition(
            position => {
                updateDriverLocation(
                    position.coords.latitude,
                    position.coords.longitude
                );
            },
            error => {
                console.warn('Location permission denied:', error);
            }
        );
    };
    
    // Update location every 30 seconds
    updateLocation();
    setInterval(updateLocation, 30000);
}

// ==================== Form Validation ====================

/**
 * Validate booking form
 * @returns {boolean} True if valid
 */
function validateBookingForm() {
    const pickupLat = parseFloat(document.querySelector('input[name="pickup_lat"]').value);
    const pickupLon = parseFloat(document.querySelector('input[name="pickup_lon"]').value);
    const dropoffLat = parseFloat(document.querySelector('input[name="dropoff_lat"]').value);
    const dropoffLon = parseFloat(document.querySelector('input[name="dropoff_lon"]').value);
    const goodsType = document.querySelector('select[name="goods_type"]').value;
    const weight = parseInt(document.querySelector('input[name="weight_kg"]').value);
    
    let errors = [];
    
    if (!pickupLat || !pickupLon) errors.push('Pickup location is required');
    if (!dropoffLat || !dropoffLon) errors.push('Dropoff location is required');
    if (!goodsType) errors.push('Goods type is required');
    if (weight <= 0) errors.push('Weight must be greater than 0');
    
    if (errors.length > 0) {
        errors.forEach(error => showNotification(error, 'danger'));
        return false;
    }
    
    return true;
}

// ==================== Initialize ====================

document.addEventListener('DOMContentLoaded', function() {
    // Enable location tracking for drivers
    if (document.body.dataset.userRole === 'driver') {
        enableLocationTracking();
    }
});

// ==================== Export ====================

window.calculateFare = calculateFare;
window.updateFareEstimate = updateFareEstimate;
window.loadAvailableDrivers = loadAvailableDrivers;
window.acceptBooking = acceptBooking;
window.completeBooking = completeBooking;
window.cancelBooking = cancelBooking;
window.toggleAvailability = toggleAvailability;
window.validateBookingForm = validateBookingForm;