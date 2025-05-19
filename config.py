import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get("SESSION_SECRET", "lifesaver-organ-donation-key")
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///organ_donation.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Mail configuration for OTP verification
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'organapp12345@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'mceh bzzu hheq tyld')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'Organ Donation System <organapp12345@gmail.com>')
    MAIL_DEBUG = True  # Enable debug mode for detailed logging
    
    # OTP configuration
    OTP_EXPIRY_MINUTES = 10
