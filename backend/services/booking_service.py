"""
Booking Service

This module handles all booking-related business logic:
- Creating new bookings
- Accepting bookings
- Updating booking status
- Finding available drivers
- Calculating driver distances
"""

from datetime import datetime
from models import db, Booking, Driver, User
from services.pricing_service import estimate_fare, haversine_distance


def create_booking(farmer_id, pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, 
                   goods_type, weight_kg):
    """
    Create a new booking
    
    Called when a farmer submits a booking request
    
    Steps:
    1. Calculate estimated fare
    2. Create Booking record with status='PENDING'
    3. Save to database
    
    Args:
        farmer_id: ID of farmer creating booking
        pickup_lat, pickup_lon: Pickup location
        dropoff_lat, dropoff_lon: Dropoff location
        goods_type: Type of goods (Rice, Wheat, etc.)
        weight_kg: Weight in kg
        
    Returns:
        Booking: Created booking object
    """
    
    # Calculate estimated fare
    fare_estimate = estimate_fare(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, weight_kg)
    
    # Create new booking
    booking = Booking(
        farmer_id=farmer_id,
        pickup_latitude=pickup_lat,
        pickup_longitude=pickup_lon,
        dropoff_latitude=dropoff_lat,
        dropoff_longitude=dropoff_lon,
        goods_type=goods_type,
        weight_kg=weight_kg,
        estimated_fare=fare_estimate['total_fare'],
        status='PENDING',
        created_at=datetime.utcnow()
    )
    
    # Save to database
    db.session.add(booking)
    db.session.commit()
    
    return booking


def accept_booking(booking_id, driver_id):
    """
    Accept a booking as a driver
    
    Called when driver clicks "Accept Booking" button
    
    Steps:
    1. Find the booking
    2. Verify it's still PENDING
    3. Assign driver to booking
    4. Change status to ACCEPTED
    5. Record acceptance time
    6. Save to database
    
    Args:
        booking_id: ID of booking to accept
        driver_id: ID of driver accepting
        
    Returns:
        Booking: Updated booking object
    """
    
    # Find the booking
    booking = Booking.query.get(booking_id)
    
    if not booking:
        raise Exception('Booking not found')
    
    if booking.status != 'PENDING':
        raise Exception('Booking is not available')
    
    if booking.driver_id is not None:
        raise Exception('Booking already has a driver')
    
    # Get driver info to check capacity
    driver = Driver.query.filter_by(user_id=driver_id).first()
    
    if not driver:
        raise Exception('Driver profile not found')
    
    if driver.capacity_kg < booking.weight_kg:
        raise Exception('Vehicle capacity too low for this booking')
    
    # Update booking
    booking.driver_id = driver_id
    booking.status = 'ACCEPTED'
    booking.accepted_at = datetime.utcnow()
    
    # Save to database
    db.session.commit()
    
    return booking


def complete_booking(booking_id, final_fare=None):
    """
    Mark a booking as completed
    
    Called when driver finishes the transportation
    
    Args:
        booking_id: ID of booking to complete
        final_fare: Optional final fare (if different from estimate)
        
    Returns:
        Booking: Updated booking object
    """
    
    booking = Booking.query.get(booking_id)
    
    if not booking:
        raise Exception('Booking not found')
    
    if booking.status not in ['ACCEPTED']:
        raise Exception('Can only complete accepted bookings')
    
    # Update booking
    booking.status = 'COMPLETED'
    booking.completed_at = datetime.utcnow()
    
    # Set final fare (use estimate if not provided)
    if final_fare:
        booking.final_fare = final_fare
    else:
        booking.final_fare = booking.estimated_fare
    
    # Update driver earnings
    if booking.driver_id:
        driver = Driver.query.filter_by(user_id=booking.driver_id).first()
        if driver:
            driver.total_earnings = (driver.total_earnings or 0) + booking.final_fare
    
    db.session.commit()
    
    return booking


def get_available_drivers(pickup_lat, pickup_lon, weight_kg, max_distance_km=50):
    """
    Find available drivers near pickup location
    
    Steps:
    1. Query all online drivers
    2. Filter by vehicle capacity
    3. Calculate distance from pickup
    4. Return sorted by distance
    
    Args:
        pickup_lat, pickup_lon: Pickup location
        weight_kg: Weight to be transported
        max_distance_km: Maximum distance to search (default 50 km)
        
    Returns:
        List of tuples: [(Driver, distance_km), ...]
                        Sorted by distance (nearest first)
    """
    
    # Get all online drivers with sufficient capacity
    drivers = Driver.query.filter(
        Driver.is_available == True,
        Driver.capacity_kg >= weight_kg,
        Driver.latitude != None,
        Driver.longitude != None
    ).all()
    
    # Calculate distance and filter
    available_drivers = []
    
    for driver in drivers:
        distance = haversine_distance(
            pickup_lat, pickup_lon,
            driver.latitude, driver.longitude
        )
        
        # Only include drivers within search radius
        if distance <= max_distance_km:
            available_drivers.append((driver, distance))
    
    # Sort by distance (nearest first)
    available_drivers.sort(key=lambda x: x[1])
    
    return available_drivers


def cancel_booking(booking_id):
    """
    Cancel a booking
    
    Args:
        booking_id: ID of booking to cancel
        
    Returns:
        Booking: Updated booking object
    """
    
    booking = Booking.query.get(booking_id)
    
    if not booking:
        raise Exception('Booking not found')
    
    if booking.status in ['COMPLETED', 'CANCELLED']:
        raise Exception('Cannot cancel completed or already cancelled bookings')
    
    # Update status
    booking.status = 'CANCELLED'
    db.session.commit()
    
    return booking


def get_booking_details(booking_id):
    """
    Get detailed information about a booking including farmer and driver info
    
    Args:
        booking_id: ID of booking
        
    Returns:
        dict: Booking details with related info
    """
    
    booking = Booking.query.get(booking_id)
    
    if not booking:
        return None
    
    # Get farmer info
    farmer = User.query.get(booking.farmer_id)
    
    # Get driver info (if assigned)
    driver = None
    driver_user = None
    if booking.driver_id:
        driver_user = User.query.get(booking.driver_id)
        driver = Driver.query.filter_by(user_id=booking.driver_id).first()
    
    return {
        'booking': booking,
        'farmer': farmer,
        'driver': driver,
        'driver_user': driver_user
    }