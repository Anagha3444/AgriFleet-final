"""
Database Models using SQLAlchemy ORM

Models:
- User: Login accounts (farmers, drivers, admins)
- Driver: Extended driver information
- Booking: Transportation requests
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    """
    User Model - Represents a user account
    
    Can be: Farmer, Driver, or Admin
    """
    __tablename__ = 'users'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='farmer')
    full_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    driver = db.relationship('Driver', back_populates='user', uselist=False, cascade='all, delete-orphan')
    farmer_bookings = db.relationship('Booking', foreign_keys='Booking.farmer_id', back_populates='farmer', cascade='all, delete-orphan')
    driver_bookings = db.relationship('Booking', foreign_keys='Booking.driver_id', back_populates='driver_user', cascade='all, delete-orphan')
    
    # Methods
    def set_password(self, password):
        """Hash and store password securely"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_farmer(self):
        """Check if user is a farmer"""
        return self.role == 'farmer'
    
    def is_driver(self):
        """Check if user is a driver"""
        return self.role == 'driver'
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Driver(db.Model):
    """
    Driver Model - Extended information for drivers
    
    Links to User with role='driver'
    """
    __tablename__ = 'drivers'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(100), nullable=False)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False)
    capacity_kg = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    total_earnings = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='driver')
    
    def __repr__(self):
        return f'<Driver {self.vehicle_number}>'


class Booking(db.Model):
    """
    Booking Model - Transportation request from farmer
    
    Status flow: PENDING → ACCEPTED → COMPLETED or CANCELLED
    """
    __tablename__ = 'bookings'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Locations
    pickup_latitude = db.Column(db.Float, nullable=False)
    pickup_longitude = db.Column(db.Float, nullable=False)
    dropoff_latitude = db.Column(db.Float, nullable=False)
    dropoff_longitude = db.Column(db.Float, nullable=False)
    
    # Goods details
    goods_type = db.Column(db.String(255), nullable=False)
    weight_kg = db.Column(db.Integer, nullable=False)
    
    # Pricing
    estimated_fare = db.Column(db.Float, nullable=False)
    final_fare = db.Column(db.Float)
    
    # Status and timestamps
    status = db.Column(db.String(20), default='PENDING', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    farmer = db.relationship('User', foreign_keys=[farmer_id], back_populates='farmer_bookings')
    driver_user = db.relationship('User', foreign_keys=[driver_id], back_populates='driver_bookings')
    
    # Methods
    def is_pending(self):
        """Check if booking is pending"""
        return self.status == 'PENDING'
    
    def is_accepted(self):
        """Check if booking is accepted"""
        return self.status == 'ACCEPTED'
    
    def is_completed(self):
        """Check if booking is completed"""
        return self.status == 'COMPLETED'
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'