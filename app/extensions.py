"""
Flask extensions initialization.
Extensions are initialized here but configured in the app factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions (but don't configure yet)
db = SQLAlchemy()
login_manager = LoginManager()

# Configure login manager
login_manager.login_view = 'core.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
