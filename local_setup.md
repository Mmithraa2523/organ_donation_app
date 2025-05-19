# Local Setup Instructions for Lifesaver: Organ & Blood Donation System

Follow these detailed instructions to set up and run the Organ & Blood Donation System on your local machine.

## Prerequisites

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **PostgreSQL** - [Download PostgreSQL](https://www.postgresql.org/download/)
3. **Git** (optional, for cloning the repository)

## Step 1: Download and Prepare the Application

### Option 1: Download as a ZIP file from Replit
1. Download the project files from Replit
2. Extract the ZIP file to your preferred location

### Option 2: Clone from a Git repository (if available)
```bash
git clone https://github.com/yourusername/lifesaver.git
cd lifesaver
```

## Step 2: Create a Virtual Environment

Creating a virtual environment isolates your project dependencies from other Python projects.

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux
```bash
python -m venv venv
source venv/bin/activate
```

## Step 3: Install Required Dependencies

```bash
pip install flask flask-login flask-mail flask-sqlalchemy flask-wtf email-validator psycopg2-binary twilio sendgrid sqlalchemy wtforms gunicorn
```

## Step 4: Set Up PostgreSQL Database

### PostgreSQL Installation Verification
First, make sure PostgreSQL is properly installed and running:

- **Windows**: Check if PostgreSQL service is running in Services
- **macOS**: Run `brew services list | grep postgres`
- **Linux**: Run `sudo systemctl status postgresql`

### Create Database and User
1. Open the PostgreSQL command line:
   
   ```bash
   # Windows (open command prompt as administrator)
   psql -U postgres
   
   # macOS/Linux
   sudo -u postgres psql
   ```

2. Create a database and user:
   
   ```sql
   CREATE DATABASE organ_donation;
   CREATE USER lifesaver WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE organ_donation TO lifesaver;
   \q
   ```

## Step 5: Configure Environment Variables

Create a file named `.env` in the project's root directory with the following content:

```
# Database configuration
DATABASE_URL=postgresql://lifesaver:your_secure_password@localhost:5432/organ_donation

# Flask configuration
FLASK_APP=main.py
FLASK_ENV=development
SESSION_SECRET=your_random_secret_key

# Email configuration (for OTP delivery)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com

# Twilio configuration (optional, for SMS notifications)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_phone
```

### Notes on Email Configuration:
* For Gmail, you need to generate an "App Password" if you have 2FA enabled
* Go to your Google Account → Security → App passwords
* Select "Mail" and "Other (Custom name)" → enter "Lifesaver App"
* Use the generated password in your `.env` file

## Step 6: Set Up the Database Schema

Run the following commands to initialize the database:

```bash
# First, make sure to create the database initialization script
cat > init_db.py << EOF
import os
from app import app, db
from models import Role, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
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
            print("Database initialization complete!")
        else:
            print("Database already initialized!")

if __name__ == "__main__":
    init_database()
EOF

# Run the initialization script
python init_db.py
```

## Step 7: Run the Application

```bash
python main.py
```

This will start the application on http://localhost:5000

## Step 8: Access the Application

Open your web browser and navigate to: http://localhost:5000

### Default Admin Login:
- Email: admin@lifesaver.com
- Password: admin123

## Common Issues and Solutions

### Database Connection Issues

1. **Connection Refused Error**:
   - Make sure PostgreSQL service is running
   - Check if the port number in DATABASE_URL is correct (default: 5432)
   - Verify there's no firewall blocking the connection

2. **Authentication Failed**:
   - Double-check username and password in DATABASE_URL
   - Ensure the user has proper privileges on the database

3. **Database Does Not Exist**:
   - Make sure you created the database as specified in Step 4

### Email Sending Issues

1. **SMTP Authentication Error**:
   - For Gmail: Make sure you're using an App Password, not your regular password
   - Verify MAIL_USERNAME and MAIL_PASSWORD in .env file

2. **Connection Timeout**:
   - Check your internet connection
   - Some networks block SMTP ports; try using a different network

### Application Setup Issues

1. **Module Not Found Errors**:
   - Make sure you've installed all dependencies from Step 3
   - Verify that you're running Python from the virtual environment

2. **Permission Errors on Linux/macOS**:
   - Run `chmod +x main.py` to make the script executable

## Project Structure Overview

```
.
├── app.py                 # Application configuration
├── config.py              # Configuration settings
├── forms.py               # WTForms definitions
├── main.py                # Application entry point
├── models.py              # Database models
├── utils.py               # Utility functions
├── routes/                # Route handlers
│   ├── __init__.py
│   ├── admin.py           # Admin routes
│   ├── auth.py            # Authentication routes
│   ├── doctor.py          # Doctor routes
│   └── user.py            # User routes
├── static/                # Static assets
│   ├── css/               # CSS stylesheets
│   ├── js/                # JavaScript files
│   └── img/               # Images
└── templates/             # Jinja2 templates
    ├── admin/             # Admin templates
    ├── auth/              # Authentication templates
    ├── doctor/            # Doctor templates
    ├── user/              # User templates
    └── layout.html        # Base template
```