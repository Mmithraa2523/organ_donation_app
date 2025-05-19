from flask import render_template, Blueprint
from app import app

# Define main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('index.html', scroll_to='about')

@app.route('/contact')
def contact():
    return render_template('index.html', scroll_to='contact')
