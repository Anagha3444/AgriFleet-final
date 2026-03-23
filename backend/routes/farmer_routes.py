"""
Farmer Routes

Handles farmer-specific operations: creating bookings, viewing bookings, etc.

Routes:
  GET  /farmer/dashboard              - Farmer dashboard
  GET  /farmer/create-booking         - Create booking form
  POST /farmer/create-booking         - Process booking creation
  GET  /farmer/booking/<id>           - View booking details
  GET  /farmer/bookings               - View all farmer's bookings
  GET  /farmer/api/estimate-fare      - Calculate fare estimate (AJAX)
  POST /farmer/booking/<id>/cancel    - Cancel a booking
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Booking, Driver, User
from auth import farmer_required, get_current_user
from services.pricing_service import estimate_fare
from services.booking_service import (
    create_booking, get_available_drivers, get_booking_details, cancel_booking
)

# Create blueprint
farmer_bp = Blueprint('farmer', __name__, url_prefix='/farmer')


@farmer_bp.route('/dashboard')
@farmer_required
def dashboard():
    """
    Farmer dashboard showing recent bookings and statistics
    """
    current_user = get_current_user()
    
    # Get recent bookings
    recent_bookings = Booking.query.filter_by(farmer_id=current_user.id).order_by(
        Booking.created_at.desc()
    ).limit(10).all()
    
    # Calculate statistics
    total_bookings = Booking.query.filter_by(farmer_id=current_user.id).count()
    completed = Booking.query.filter_by(farmer_id=current_user.id, status='COMPLETED').count()
    pending = Booking.query.filter_by(farmer_id=current_user.id, status='PENDING').count()
    
    stats = {
        'total_bookings': total_bookings,
        'completed': completed,
        'pending': pending,
        'active': Booking.query.filter_by(farmer_id=current_user.id, status='ACCEPTED').count()
    }
    
    return render_template(
        'farmer/dashboard.html',
        recent_bookings=recent_bookings,
        stats=stats
    )


@farmer_bp.route('/create-booking', methods=['GET', 'POST'])
@farmer_required
def create_booking_page():
    """
    Create new transportation booking
    
    GET:  Show booking form
    POST: Process booking creation
    """
    
    if request.method == 'GET':
        return render_template('farmer/create_booking.html')
    
    # Handle POST request
    current_user = get_current_user()
    
    try:
        # Get form data
        pickup_lat = float(request.form.get('pickup_lat'))
        pickup_lon = float(request.form.get('pickup_lon'))
        dropoff_lat = float(request.form.get('dropoff_lat'))
        dropoff_lon = float(request.form.get('dropoff_lon'))
        goods_type = request.form.get('goods_type', '').strip()
        weight_kg = int(request.form.get('weight_kg'))
        
        # Validation
        if not goods_type:
            flash('Please specify goods type', 'danger')
            return redirect(url_for('farmer.create_booking_page'))
        
        if weight_kg <= 0:
            flash('Weight must be greater than 0', 'danger')
            return redirect(url_for('farmer.create_booking_page'))
        
        # Create booking using service
        booking = create_booking(
            current_user.id,
            pickup_lat, pickup_lon,
            dropoff_lat, dropoff_lon,
            goods_type, weight_kg
        )
        
        flash(f'Booking created! Estimated fare: ₹{booking.estimated_fare}', 'success')
        return redirect(url_for('farmer.booking_details', booking_id=booking.id))
    
    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'danger')
        return redirect(url_for('farmer.create_booking_page'))
    except Exception as e:
        flash(f'Error creating booking: {str(e)}', 'danger')
        return redirect(url_for('farmer.create_booking_page'))


@farmer_bp.route('/booking/<int:booking_id>')
@farmer_required
def booking_details(booking_id):
    """
    View detailed information about a specific booking
    """
    current_user = get_current_user()
    
    booking = Booking.query.get(booking_id)
    
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('farmer.dashboard'))
    
    # Check authorization (farmer can only view their own bookings)
    if booking.farmer_id != current_user.id:
        flash('You cannot view this booking', 'danger')
        return redirect(url_for('farmer.dashboard'))
    
    # Get driver info if assigned
    driver = None
    if booking.driver_id:
        driver = Driver.query.filter_by(user_id=booking.driver_id).first()
    
    return render_template(
        'farmer/booking_details.html',
        booking=booking,
        driver=driver
    )


@farmer_bp.route('/bookings')
@farmer_required
def bookings():
    """
    View all bookings made by current farmer
    """
    current_user = get_current_user()
    
    # Get status filter from query parameter
    status_filter = request.args.get('status', None)
    
    # Build query
    query = Booking.query.filter_by(farmer_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    bookings_list = query.order_by(Booking.created_at.desc()).all()
    
    return render_template(
        'farmer/history.html',
        bookings=bookings_list,
        current_status=status_filter
    )


@farmer_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@farmer_required
def cancel_booking_handler(booking_id):
    """
    Cancel a pending booking
    """
    current_user = get_current_user()
    
    booking = Booking.query.get(booking_id)
    
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('farmer.dashboard'))
    
    if booking.farmer_id != current_user.id:
        flash('You cannot cancel this booking', 'danger')
        return redirect(url_for('farmer.dashboard'))
    
    try:
        cancel_booking(booking_id)
        flash('Booking cancelled', 'info')
    except Exception as e:
        flash(f'Cannot cancel: {str(e)}', 'danger')
    
    return redirect(url_for('farmer.booking_details', booking_id=booking_id))


# ==================== AJAX API Endpoints ====================

@farmer_bp.route('/api/estimate-fare', methods=['POST'])
@farmer_required
def api_estimate_fare():
    """
    Calculate estimated fare
    
    AJAX endpoint called by JavaScript
    
    Returns JSON with fare breakdown
    """
    try:
        data = request.get_json()
        
        pickup_lat = float(data.get('pickup_lat'))
        pickup_lon = float(data.get('pickup_lon'))
        dropoff_lat = float(data.get('dropoff_lat'))
        dropoff_lon = float(data.get('dropoff_lon'))
        weight_kg = int(data.get('weight_kg'))
        
        # Calculate fare
        fare = estimate_fare(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, weight_kg)
        
        return jsonify({
            'success': True,
            'fare': fare
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@farmer_bp.route('/api/available-drivers', methods=['POST'])
@farmer_required
def api_available_drivers():
    """
    Get list of available drivers near pickup location
    
    AJAX endpoint called by JavaScript
    
    Returns JSON with list of nearby drivers
    """
    try:
        data = request.get_json()
        
        pickup_lat = float(data.get('pickup_lat'))
        pickup_lon = float(data.get('pickup_lon'))
        weight_kg = int(data.get('weight_kg'))
        
        # Find available drivers
        available = get_available_drivers(pickup_lat, pickup_lon, weight_kg)
        
        # Format response
        drivers_list = []
        for driver, distance in available:
            user = User.query.get(driver.user_id)
            drivers_list.append({
                'id': driver.id,
                'name': user.full_name if user else 'Unknown',
                'vehicle': f"{driver.vehicle_type} ({driver.vehicle_number})",
                'distance_km': round(distance, 2),
                'capacity_kg': driver.capacity_kg
            })
        
        return jsonify({
            'success': True,
            'drivers': drivers_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400