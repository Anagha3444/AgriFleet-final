"""
Database Initialization Script

This script:
1. Creates all database tables
2. Inserts sample test data
3. Can be run multiple times safely

Usage:
    python database/init_db.py
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Driver
from datetime import datetime


def init_database():
    """
    Initialize database with tables and sample data
    """
    
    with app.app_context():
        # Drop existing tables (for fresh start)
        print(" Initializing database...")
        db.drop_all()
        print(" Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print(" Created database tables")
        
        # ==================== Create Sample Users ====================
        
        # Sample Farmer
        farmer = User(
            email='farmer@example.com',
            full_name='Raj Kumar (Farmer)',
            phone_number='9876543210',
            role='farmer'
        )
        farmer.set_password('password123')
        db.session.add(farmer)
        
        # Sample Driver
        driver_user = User(
            email='driver@example.com',
            full_name='Suresh Singh (Driver)',
            phone_number='9876543211',
            role='driver'
        )
        driver_user.set_password('password123')
        db.session.add(driver_user)
        
        # Admin (optional)
        admin = User(
            email='admin@example.com',
            full_name='Admin User',
            phone_number='9876543212',
            role='admin'
        )
        admin.set_password('password123')
        db.session.add(admin)
        
        # Save users first
        db.session.commit()
        print(" Created sample users")
        
        # ==================== Create Driver Profile ====================
        
        driver = Driver(
            user_id=driver_user.id,
            vehicle_type='Truck',
            vehicle_number='DL-01-AB-1234',
            capacity_kg=5000,
            is_available=True,
            latitude=19.0760,      # Mumbai
            longitude=72.8777,
            total_earnings=0
        )
        db.session.add(driver)
        db.session.commit()
        print(" Created driver profile")
        
        # ==================== Print Summary ====================
        print("\n" + "="*60)
        print(" Database initialized successfully!")
        print("="*60)
        print("\nSample User Accounts:")
        print("\n FARMER ACCOUNT:")
        print("   Email:    farmer@example.com")
        print("   Password: password123")
        print("\n DRIVER ACCOUNT:")
        print("   Email:    driver@example.com")
        print("   Password: password123")
        print("\n ADMIN ACCOUNT:")
        print("   Email:    admin@example.com")
        print("   Password: password123")
        print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n Error initializing database: {e}")
        sys.exit(1)