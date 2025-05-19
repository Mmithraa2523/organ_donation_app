"""
Local Environment Setup Guide for Lifesaver: Organ & Blood Donation System
-------------------------------------------------------------------------
This script will guide you through setting up the application on your local machine.
It provides instructions and a menu-based interface to help with installation.
"""

import os
import sys
import platform
import subprocess
import webbrowser

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header"""
    clear_screen()
    print("=" * 70)
    print("  LIFESAVER: ORGAN & BLOOD DONATION SYSTEM - LOCAL SETUP GUIDE")
    print("=" * 70)
    print()

def detect_os():
    """Detect the operating system"""
    system = platform.system()
    if system == "Windows":
        return "Windows"
    elif system == "Darwin":
        return "macOS"
    elif system == "Linux":
        return "Linux"
    else:
        return "Unknown"

def show_prerequisites(os_type):
    """Show prerequisites for the detected OS"""
    print_header()
    print(f"PREREQUISITES FOR {os_type.upper()}")
    print("=" * 30)
    print()
    
    if os_type == "Windows":
        print("1. Python 3.8+ - Download from https://www.python.org/downloads/windows/")
        print("   - During installation, check 'Add Python to PATH'")
        print()
        print("2. PostgreSQL - Download from https://www.postgresql.org/download/windows/")
        print("   - Remember the password you set for the 'postgres' user")
        print("   - Keep the default port (5432)")
    
    elif os_type == "macOS":
        print("1. Python 3.8+ - Download from https://www.python.org/downloads/mac-osx/")
        print("   - Verify installation with: python3 --version")
        print()
        print("2. PostgreSQL - Install using Homebrew or download installer")
        print("   - Homebrew: brew install postgresql && brew services start postgresql")
        print("   - Or download from https://www.postgresql.org/download/macosx/")
    
    elif os_type == "Linux":
        print("1. Python 3.8+ - Install using package manager")
        print("   - sudo apt update && sudo apt install python3 python3-pip python3-venv")
        print()
        print("2. PostgreSQL - Install using package manager")
        print("   - sudo apt install postgresql postgresql-contrib")
        print("   - sudo systemctl start postgresql && sudo systemctl enable postgresql")
    
    print()
    input("Press Enter when you have installed these prerequisites...")

def setup_virtual_env(os_type):
    """Show instructions for setting up virtual environment"""
    print_header()
    print("SETTING UP VIRTUAL ENVIRONMENT")
    print("=" * 30)
    print()
    
    if os_type == "Windows":
        print("Run the following commands in Command Prompt/PowerShell:")
        print("1. Navigate to your project folder")
        print("   cd path\\to\\lifesaver")
        print()
        print("2. Create virtual environment")
        print("   python -m venv venv")
        print()
        print("3. Activate virtual environment")
        print("   venv\\Scripts\\activate")
    
    elif os_type in ["macOS", "Linux"]:
        print("Run the following commands in Terminal:")
        print("1. Navigate to your project folder")
        print("   cd path/to/lifesaver")
        print()
        print("2. Create virtual environment")
        print("   python3 -m venv venv")
        print()
        print("3. Activate virtual environment")
        print("   source venv/bin/activate")
    
    print()
    input("Press Enter when you have set up your virtual environment...")

def install_packages(os_type):
    """Show instructions for installing packages"""
    print_header()
    print("INSTALLING REQUIRED PACKAGES")
    print("=" * 30)
    print()
    
    print("With your virtual environment activated, run:")
    print()
    print("pip install flask flask-login flask-mail flask-sqlalchemy flask-wtf")
    print("pip install email-validator psycopg2-binary twilio sendgrid sqlalchemy wtforms gunicorn")
    print()
    input("Press Enter when you have installed all required packages...")

def db_setup_instructions(os_type):
    """Show instructions for database setup"""
    print_header()
    print("DATABASE SETUP")
    print("=" * 30)
    print()
    
    print("1. Run the database setup script in your project folder:")
    if os_type == "Windows":
        print("   cd local_setup")
        print("   python database_setup.py")
    else:
        print("   cd local_setup")
        print("   python database_setup.py")
    
    print()
    print("2. The script will:")
    print("   - Create a PostgreSQL database and user")
    print("   - Generate a .env file with the database connection string")
    print()
    print("3. After the script completes, run the initialization script:")
    if os_type == "Windows":
        print("   cd ..")
        print("   python init_db.py")
    else:
        print("   cd ..")
        print("   python init_db.py")
    
    print()
    input("Press Enter when you have completed database setup...")

def env_file_instructions():
    """Show instructions for .env file setup"""
    print_header()
    print("ENVIRONMENT CONFIGURATION (.env FILE)")
    print("=" * 30)
    print()
    
    print("Ensure your .env file in the root project folder contains:")
    print()
    print("# Database configuration")
    print("DATABASE_URL=postgresql://lifesaver:your_password@localhost:5432/organ_donation")
    print()
    print("# Flask configuration")
    print("FLASK_APP=main.py")
    print("FLASK_ENV=development")
    print("SESSION_SECRET=your_secret_key")
    print()
    print("# Email configuration (for OTP delivery)")
    print("MAIL_USERNAME=your_email@gmail.com")
    print("MAIL_PASSWORD=your_app_password")
    print("MAIL_DEFAULT_SENDER=your_email@gmail.com")
    print()
    print("Note: For Gmail, you need to create an App Password if you have 2FA enabled")
    print("Go to: Google Account > Security > App passwords")
    print()
    input("Press Enter when you have configured your .env file...")

def run_application(os_type):
    """Show instructions for running the application"""
    print_header()
    print("RUNNING THE APPLICATION")
    print("=" * 30)
    print()
    
    print("With your virtual environment activated, run:")
    print()
    if os_type == "Windows":
        print("python local_setup\\local_main.py")
    else:
        print("python local_setup/local_main.py")
    print()
    print("This will start the application on http://localhost:5000")
    print()
    print("You can login with the default admin credentials:")
    print("Email: admin@lifesaver.com")
    print("Password: admin123")
    print()
    input("Press Enter when you're ready to proceed...")

def show_troubleshooting():
    """Show troubleshooting tips"""
    print_header()
    print("TROUBLESHOOTING COMMON ISSUES")
    print("=" * 30)
    print()
    
    print("DATABASE CONNECTION ISSUES:")
    print("1. Make sure PostgreSQL service is running")
    print("2. Verify username and password in .env file match what you created")
    print("3. Check that the database exists and user has proper permissions")
    print()
    print("EMAIL CONFIGURATION ISSUES:")
    print("1. For Gmail, use an App Password instead of your regular password")
    print("2. Verify MAIL_USERNAME and MAIL_PASSWORD in .env file")
    print("3. Check your internet connection and firewall settings")
    print()
    print("PYTHON/PACKAGE ISSUES:")
    print("1. Ensure you're running from the virtual environment")
    print("2. Make sure all required packages are installed")
    print("3. If port 5000 is already in use, change the port in local_main.py")
    print()
    input("Press Enter to return to the main menu...")

def open_docs():
    """Open documentation in web browser"""
    try:
        webbrowser.open("https://github.com/yourusername/lifesaver")
    except:
        print("Could not open web browser automatically.")
        print("Please visit: https://github.com/yourusername/lifesaver")
    input("Press Enter to continue...")

def main_menu():
    """Display the main menu"""
    os_type = detect_os()
    
    while True:
        print_header()
        print(f"Detected OS: {os_type}")
        print()
        print("SETUP GUIDE - MAIN MENU")
        print("=" * 30)
        print()
        print("1. Check Prerequisites")
        print("2. Set Up Virtual Environment")
        print("3. Install Required Packages")
        print("4. Database Setup Instructions")
        print("5. Environment Configuration (.env file)")
        print("6. Run the Application")
        print("7. Troubleshooting Guide")
        print("8. Exit")
        print()
        
        choice = input("Enter your choice (1-8): ")
        
        if choice == "1":
            show_prerequisites(os_type)
        elif choice == "2":
            setup_virtual_env(os_type)
        elif choice == "3":
            install_packages(os_type)
        elif choice == "4":
            db_setup_instructions(os_type)
        elif choice == "5":
            env_file_instructions()
        elif choice == "6":
            run_application(os_type)
        elif choice == "7":
            show_troubleshooting()
        elif choice == "8":
            print_header()
            print("Thank you for using the Lifesaver setup guide!")
            print("For more information, refer to the README.md file.")
            print()
            print("If you encounter any issues, please check the troubleshooting guide")
            print("or submit an issue on the project repository.")
            print()
            input("Press Enter to exit...")
            break
        else:
            input("Invalid choice. Press Enter to try again...")

if __name__ == "__main__":
    main_menu()