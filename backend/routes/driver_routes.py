"""
Driver Routes

Handles driver-specific operations: viewing available bookings, accepting bookings, etc.

Routes:
  GET  /driver/dashboard              - Driver dashboard
  GET  /driver/available              - View available bookings
  GET  /driver/booking/<id>           - View booking details
  POST /driver/accept/<booking_id>    - Accept a booking
  POST /driver/complete/<booking_id>  - Mark booking as completed
  GET  /driver/bookings               - View all driver's bookings
  POST /driver/api/toggle-availability - Go online/offline (AJAX)
  POST /driver/api/update-location    - Update location (AJAX)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Booking, Driver, User
from auth import driver_required, get_current_user
from services.booking_service import accept_booking, complete_booking, get_booking_details

# Create blueprint
driver_bp = Blueprint('driver', __name__, url_prefix='/driver')


@driver_bp.route('/dashboard')
@driver_required
def dashboard():
    """
    Driver dashboard showing available bookings and statistics
    """
    current_user = get_current_user()
    
    # Get driver profile
    driver = Driver.query.filter_by(user_id=current_user.id).first()
    
    if not driver:
        flash('Driver profile not found', 'danger')
        return redirect(url_for('index'))
    
    # Get pending bookings (available for this driver)
    pending_bookings = Booking.query.filter(
        Booking.status == 'PENDING',
        Booking.driver_id == None  # Not yet assigned
    ).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get active bookings (assigned to this driver)
    active_bookings = Booking.query.filter(
        Booking.driver_id == current_user.id,
        Booking.status.in_(['ACCEPTED'])
    ).all()
    
    # Calculate statistics
    completed = Booking.query.filter_by(driver_id=current_user.id, status='COMPLETED').count()
    
    stats = {
        'available': len(pending_bookings),
        'active': len(active_bookings),
        'completed': completed,
        'earnings': driver.total_earnings or 0
    }
    
    return render_template(
        'driver/dashboard.html',
        driver=driver,
        pending_bookings=pending_bookings,
        active_bookings=active_bookings,
        stats=stats
    )


@driver_bp.route('/available')
@driver_required
def available_bookings():
    """
    View all available bookings (PENDING status)
    
    Drivers browse this list and can accept any booking that matches their vehicle capacity
    """
    current_user = get_current_user()
    driver = Driver.query.filter_by(user_id=current_user.id).first()
    
    if not driver:
        flash('Driver profile not found', 'danger')
        return redirect(url_for('index'))
    
    # Get all pending bookings
    bookings = Booking.query.filter(
        Booking.status == 'PENDING',
        Booking.driver_id == None  # Not assigned to anyone
    ).order_by(Booking.created_at.desc()).all()
    
    return render_template(
        'driver/available_bookings.html',
        bookings=bookings,
        driver=driver
    )


@driver_bp.route('/booking/<int:booking_id>')
@driver_required
def booking_details(booking_id):
    """
    View detailed information about a specific booking
    """
    current_user = get_current_user()
    
    booking = Booking.query.get(booking_id)
    
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('driver.dashboard'))
    
    # Get detailed booking info
    details = get_booking_details(booking_id)
    
    return render_template(
        'driver/booking_details.html',
        booking=booking,
        farmer=details['farmer'],
        driver=details['driver']
    )


@driver_bp.route('/accept/<int:booking_id>', methods=['POST'])
@driver_required
def accept_booking_handler(booking_id):
    """
    Accept a booking as driver
    
    Flow:
    1. Verify booking exists and is PENDING
    2. Verify driver has sufficient capacity
    3. Assign driver to booking
    4. Change status to ACCEPTED
    5. Save to database
    """
    current_user = get_current_user()
    
    try:
        # Accept the booking
        booking = accept_booking(booking_id, current_user.id)
        
        flash(f'Booking accepted! Fare: ₹{booking.estimated_fare}', 'success')
        return redirect(url_for('driver.booking_details', booking_id=booking_id))
    
    except Exception as e:
        flash(f'Cannot accept booking: {str(e)}', 'danger')
        return redirect(url_for('driver.available_bookings'))


@driver_bp.route('/complete/<int:booking_id>', methods=['POST'])
@driver_required
def complete_booking_handler(booking_id):
    """
    Mark a booking as completed
    
    Called when driver arrives at destination
    """
    current_user = get_current_user()
    
    booking = Booking.query.get(booking_id)
    
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('driver.dashboard'))
    
    # Verify driver is assigned
    if booking.driver_id != current_user.id:
        flash('This booking is not assigned to you', 'danger')
        return redirect(url_for('driver.dashboard'))
    
    try:
        booking = complete_booking(booking_id)
        flash(f'Booking completed! Earned: ₹{booking.final_fare}', 'success')
        return redirect(url_for('driver.dashboard'))
    
    except Exception as e:
        flash(f'Error completing booking: {str(e)}', 'danger')
        return redirect(url_for('driver.booking_details', booking_id=booking_id))


@driver_bp.route('/bookings')
@driver_required
def bookings():
    """
    View all bookings accepted by current driver
    """
    current_user = get_current_user()
    
    # Get status filter from query parameter
    status_filter = request.args.get('status', None)
    
    # Build query
    query = Booking.query.filter_by(driver_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    bookings_list = query.order_by(Booking.created_at.desc()).all()
    
    return render_template(
        'driver/history.html',
        bookings=bookings_list,
        current_status=status_filter
    )


# ==================== AJAX API Endpoints ====================

@driver_bp.route('/api/update-location', methods=['POST'])
@driver_required
def api_update_location():
    """
    Update driver's current location
    
    Called periodically by JavaScript
    
    AJAX endpoint returning JSON
    """
    current_user = get_current_user()
    
    try:
        data = request.get_json()
        
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # Get driver profile
        driver = Driver.query.filter_by(user_id=current_user.id).first()
        
        if not driver:
            return jsonify({'success': False, 'error': 'Driver not found'}), 404
        
        # Update location
        driver.latitude = latitude
        driver.longitude = longitude
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Location updated'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@driver_bp.route('/api/toggle-availability', methods=['POST'])
@driver_required
def api_toggle_availability():
    """
    Toggle driver availability (go online/offline)
    
    AJAX endpoint returning JSON
    """
    current_user = get_current_user()
    
    try:
        # Get driver profile
        driver = Driver.query.filter_by(user_id=current_user.id).first()
        
        if not driver:
            return jsonify({'success': False, 'error': 'Driver not found'}), 404
        
        # Toggle availability
        driver.is_available = not driver.is_available
        db.session.commit()
        
        status = 'online' if driver.is_available else 'offline'
        
        return jsonify({
            'success': True,
            'is_available': driver.is_available,
            'message': f'You are now {status}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400