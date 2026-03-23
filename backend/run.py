"""
Application Entry Point

Run this file to start the Flask development server:
    python run.py

The server will start on http://localhost:5000
"""

from app import app, db
from models import User, Driver, Booking

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created")
    
    # Print banner
    print("\n" + "="*60)
    print(" AgriHaul Agricultural Transportation Platform")
    print("="*60)
    print("\n Server running at: http://localhost:5000")
    print("\n Documentation: http://localhost:5000/")
    print("\n Tips:")
    print("   - Login with test accounts (see README)")
    print("   - Press CTRL+C to stop the server")
    print("\n" + "="*60 + "\n")
    
    # Start the development server
    app.run(debug=True, host='0.0.0.0', port=5000)