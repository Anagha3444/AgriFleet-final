"""
Pricing Service

Calculates transportation fares based on:
- Distance between pickup and dropoff
- Weight of goods
- Vehicle type and condition

Uses the Haversine formula to calculate distance from coordinates
"""

import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    
    The Haversine formula calculates the great-circle distance between
    two points on a sphere given their longitudes and latitudes
    
    Args:
        lat1, lon1: Starting point latitude and longitude
        lat2, lon2: Ending point latitude and longitude
        
    Returns:
        float: Distance in kilometers
        
    Example:
        >>> distance = haversine_distance(19.0760, 72.8777, 19.1136, 72.8697)
        >>> print(f"{distance:.2f} km")
        7.45 km
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Distance
    distance = R * c
    return distance


def calculate_fare(distance_km, weight_kg, vehicle_type='Truck'):
    """
    Calculate transportation fare
    
    Pricing Model:
    - Base Fare: ₹100 (fixed)
    - Distance: ₹10 per km
    - Weight: ₹0.50 per kg
    
    Total Fare = Base + (Distance × Rate) + (Weight × Rate)
    
    Args:
        distance_km: Distance in kilometers
        weight_kg: Weight of goods in kilograms
        vehicle_type: Type of vehicle (Truck, Auto, Pickup)
        
    Returns:
        dict: Contains calculated fare with breakdown
              {
                  'distance_km': float,
                  'weight_kg': int,
                  'base_fare': float,
                  'distance_charge': float,
                  'weight_charge': float,
                  'total_fare': float
              }
              
    Example:
        >>> fare = calculate_fare(50, 1000, 'Truck')
        >>> print(f"Total: ₹{fare['total_fare']}")
        Total: ₹1100.0
    """
    
    # Pricing rates
    BASE_FARE = 100
    DISTANCE_RATE = 10  # Per km
    WEIGHT_RATE = 0.50  # Per kg
    
    # Calculate components
    distance_charge = distance_km * DISTANCE_RATE
    weight_charge = weight_kg * WEIGHT_RATE
    total_fare = BASE_FARE + distance_charge + weight_charge
    
    # Round to 2 decimal places
    return {
        'distance_km': round(distance_km, 2),
        'weight_kg': weight_kg,
        'base_fare': BASE_FARE,
        'distance_charge': round(distance_charge, 2),
        'weight_charge': round(weight_charge, 2),
        'total_fare': round(total_fare, 2)
    }


def estimate_fare(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, weight_kg):
    """
    Estimate fare for a booking request
    
    This is called when a farmer creates a booking to show estimated price
    
    Args:
        pickup_lat, pickup_lon: Pickup coordinates
        dropoff_lat, dropoff_lon: Dropoff coordinates
        weight_kg: Weight in kilograms
        
    Returns:
        dict: Fare estimate with breakdown
        
    Example:
        >>> estimate = estimate_fare(19.0760, 72.8777, 19.1136, 72.8697, 500)
        >>> print(f"Estimated Fare: ₹{estimate['total_fare']}")
    """
    # Calculate distance
    distance = haversine_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
    
    # Calculate fare
    return calculate_fare(distance, weight_kg)