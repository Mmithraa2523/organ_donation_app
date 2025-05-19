import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# Create application
app = Flask(__name__)

# Load configuration
app.config.from_object('config.Config')
app.secret_key = os.environ.get("SESSION_SECRET", "lifesaver-organ-donation-key")

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Initialize mail
mail.init_app(app)

# Initialize CSRF protection
csrf.init_app(app)

# Register blueprints
with app.app_context():
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    from routes.doctor import doctor_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(doctor_bp)
    
    # Import models and create tables
    import models
    db.create_all()
    
    # Create admin user if it doesn't exist
    from models import User, Role
    from werkzeug.security import generate_password_hash
    
    # Create roles if they don't exist
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)
    
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user')
        db.session.add(user_role)
    
    doctor_role = Role.query.filter_by(name='doctor').first()
    if not doctor_role:
        doctor_role = Role(name='doctor')
        db.session.add(doctor_role)
    
    db.session.commit()
    
    # Create default admin user
    admin_user = User.query.filter_by(email='admin@organdonation.com').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@organdonation.com',
            password_hash=generate_password_hash('admin123'),
            role_id=admin_role.id,
            is_verified=True
        )
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Default admin user created")

# Import main routes directly
from routes import index, about, contact

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
