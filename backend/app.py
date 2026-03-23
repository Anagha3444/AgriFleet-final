"""
Main Flask Application

Initializes Flask app, database, and registers blueprints (routes)
"""

from flask import Flask, render_template
from config import config
from models import db, User, Driver, Booking
from routes.auth_routes import auth_bp
from routes.farmer_routes import farmer_bp
from routes.driver_routes import driver_bp
from auth import get_current_user
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_class=None):
    """
    Application factory function
    
    Creates and configures Flask app
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask: Configured Flask application
    """
    
    # Create Flask app
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Load configuration
    if config_class is None:
        config_class = config
    
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints (route groups)
    app.register_blueprint(auth_bp)
    app.register_blueprint(farmer_bp)
    app.register_blueprint(driver_bp)
    
    # Make current_user available in templates
    @app.context_processor
    def inject_user():
        return {'current_user': get_current_user()}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html'), 500
    
    # Main routes
    @app.route('/')
    def index():
        """Landing page"""
        return render_template('index.html')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info('Database tables created')
    
    return app


# Create app instance
app = create_app()


# Shell context for flask shell
@app.shell_context_processor
def make_shell_context():
    """Make models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Driver': Driver,
        'Booking': Booking
    }


if __name__ == '__main__':
    app.run(debug=True)