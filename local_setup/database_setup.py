"""
Database Setup Script for Local Environment
-------------------------------------------
This script helps setting up the database for the Lifesaver Organ & Blood Donation System
in a local environment.

Make sure PostgreSQL is installed and running before executing this script.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database configuration
DB_NAME = "organ_donation"
DB_USER = "lifesaver"
DB_PASSWORD = "12345"  # Change this to a secure password
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
    """
    Create the database and user if they don't exist
    """
    try:
        # Connect to PostgreSQL server
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user="postgres",
            password = "12345"# Default PostgreSQL superuser
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully!")
        else:
            print(f"Database '{DB_NAME}' already exists.")
        
        # Check if user exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = '{DB_USER}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating user '{DB_USER}'...")
            cursor.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}'")
            print(f"User '{DB_USER}' created successfully!")
        else:
            print(f"User '{DB_USER}' already exists.")
        
        # Grant privileges
        print(f"Granting privileges on database '{DB_NAME}' to user '{DB_USER}'...")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER}")
        print("Privileges granted successfully!")
        
        cursor.close()
        conn.close()
        
        # Generate .env file
        generate_env_file()
        
        print("\nDatabase setup completed successfully!")
        print("You can now run: python init_db.py")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def generate_env_file():
    """
    Generate a .env file with database configuration
    """
    env_content = f"""# Database configuration
DATABASE_URL=postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}

# Flask configuration
FLASK_APP=main.py
FLASK_ENV=development
SESSION_SECRET=lifesaver_session_secret_key

# Email configuration (for OTP delivery)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com

# Twilio configuration (optional, for SMS notifications)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_phone
"""
    
    # Create .env file
    try:
        with open('../.env', 'w') as env_file:
            env_file.write(env_content)
        print("Created .env file with database configuration")
        print("Please update the email and Twilio settings in the .env file")
    except Exception as e:
        print(f"Warning: Could not create .env file: {e}")
        print("Please create the .env file manually with the following content:")
        print("\n" + env_content)

if __name__ == "__main__":
    print("=== Lifesaver: Organ & Blood Donation System Database Setup ===\n")
    create_database()