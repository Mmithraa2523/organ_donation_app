# Local Setup Files

This folder contains scripts and instructions to help you set up the Lifesaver application on your local machine.

## Files Included

- **database_setup.py**: Script to create the PostgreSQL database and user
- **local_main.py**: Modified main.py file for running locally
- **installation_steps.txt**: Detailed installation instructions for Windows, macOS and Linux

## Quick Start Guide

1. Install Python 3.8+ and PostgreSQL
2. Set up a virtual environment and activate it
3. Install dependencies: flask, flask-login, flask-mail, flask-sqlalchemy, etc.
4. Run the database_setup.py script to create your database
5. Initialize the database with python init_db.py
6. Run the application with python local_setup/local_main.py
7. Access the application at http://localhost:5000

See the installation_steps.txt file for detailed instructions for your operating system.
