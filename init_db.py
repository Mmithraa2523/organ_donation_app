import os
from app import app, db
from models import Role, User, Hospital
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Initialize the database with default data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if roles already exist
        if Role.query.count() == 0:
            print("Creating roles...")
            admin_role = Role(name='admin')
            user_role = Role(name='user')
            doctor_role = Role(name='doctor')
            
            db.session.add_all([admin_role, user_role, doctor_role])
            db.session.commit()
            
            # Create default admin user
            print("Creating default admin user...")
            admin = User(
                username='admin',
                email='admin@lifesaver.com',
                password_hash=generate_password_hash('admin123'),
                role_id=admin_role.id,
                phone='1234567890',
                address='Admin Office',
                is_verified=True,
                date_registered=datetime.utcnow()
            )
            
            db.session.add(admin)
            db.session.commit()
            
            # Create sample hospitals
            print("Creating sample hospitals...")
            hospitals = [
                Hospital(
                    name='City General Hospital',
                    address='123 Main Street',
                    city='New York',
                    state='NY',
                    country='USA',
                    phone='1234567890'
                ),
                Hospital(
                    name='Memorial Medical Center',
                    address='456 Oak Avenue',
                    city='Los Angeles',
                    state='CA',
                    country='USA',
                    phone='9876543210'
                ),
                Hospital(
                    name='Central Health Institute',
                    address='789 Pine Road',
                    city='Chicago',
                    state='IL',
                    country='USA',
                    phone='5556667777'
                )
            ]
            
            db.session.add_all(hospitals)
            db.session.commit()
            
            print("Database initialization complete!")
        else:
            print("Database already initialized!")

if __name__ == "__main__":
    init_database()