from datetime import datetime
from flask_login import UserMixin
from app import db

# Role model for user roles
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    users = db.relationship('User', backref='role_info', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organ_donations = db.relationship('OrganDonation', backref='donor', lazy=True)
    organ_requests = db.relationship('OrganRequest', backref='requester', lazy=True)
    blood_donations = db.relationship('BloodDonation', backref='donor', lazy=True)
    blood_requests = db.relationship('BloodRequest', backref='requester', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_role(self):
        return self.role_info.name

# Doctor model
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    specialization = db.Column(db.String(100))
    license_number = db.Column(db.String(50))
    
    # Relationships
    user = db.relationship('User', backref='doctor_profile', lazy=True)
    assigned_organ_requests = db.relationship('OrganRequest', backref='assigned_doctor', lazy=True)
    assigned_organ_collections = db.relationship('OrganDonation', backref='collection_doctor', lazy=True)
    
    def __repr__(self):
        return f'<Doctor {self.user.username}>'

# Hospital model
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    
    # Relationships
    doctors = db.relationship('Doctor', backref='hospital', lazy=True)
    
    def __repr__(self):
        return f'<Hospital {self.name}>'

# Organ Donation model
class OrganDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organ_type = db.Column(db.String(50), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, collected, unavailable
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    collection_date = db.Column(db.DateTime)
    collection_doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    otp = db.Column(db.String(6))
    otp_verified = db.Column(db.Boolean, default=False)
    additional_info = db.Column(db.Text)
    
    # Advanced matching attributes
    donor_age = db.Column(db.Integer, nullable=True)
    hla_type = db.Column(db.String(50), nullable=True)  # Human Leukocyte Antigen type
    tissue_crossmatch = db.Column(db.String(20), nullable=True)  # positive, negative
    location_lat = db.Column(db.Float, nullable=True)  # Latitude for geographical matching
    location_lng = db.Column(db.Float, nullable=True)  # Longitude for geographical matching
    is_living_donor = db.Column(db.Boolean, default=False)  # Whether this is from a living donor
    medical_condition = db.Column(db.String(100), nullable=True)  # Any relevant medical conditions
    
    def __repr__(self):
        return f'<OrganDonation {self.organ_type} by {self.donor.username}>'

# Organ Request model
class OrganRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organ_type = db.Column(db.String(50), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    urgency_level = db.Column(db.String(20), default='normal')  # normal, urgent, critical
    status = db.Column(db.String(20), default='pending')  # pending, approved, fulfilled, unavailable
    date_requested = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    matched_donation_id = db.Column(db.Integer, db.ForeignKey('organ_donation.id'))
    additional_info = db.Column(db.Text)
    
    # Advanced matching attributes
    patient_age = db.Column(db.Integer, nullable=True)
    hla_type = db.Column(db.String(50), nullable=True)  # Human Leukocyte Antigen type
    weight_kg = db.Column(db.Float, nullable=True)  # Weight in kg for size matching
    height_cm = db.Column(db.Float, nullable=True)  # Height in cm for size matching
    medical_urgency_score = db.Column(db.Integer, nullable=True)  # 1-100 scale
    waiting_time_days = db.Column(db.Integer, nullable=True)  # Days on waiting list
    previous_transplants = db.Column(db.Integer, default=0)  # Number of previous transplants
    location_lat = db.Column(db.Float, nullable=True)  # Latitude for geographical matching
    location_lng = db.Column(db.Float, nullable=True)  # Longitude for geographical matching
    medical_condition = db.Column(db.String(100), nullable=True)  # Any relevant medical conditions
    
    # Relationship for matched donation
    matched_donation = db.relationship('OrganDonation', backref='matched_request', lazy=True, foreign_keys=[matched_donation_id])
    
    def __repr__(self):
        return f'<OrganRequest {self.organ_type} by {self.requester.username}>'

# Blood Donation model
class BloodDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    quantity_ml = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  # pending, approved, collected
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    collection_date = db.Column(db.DateTime)
    otp = db.Column(db.String(6))
    otp_verified = db.Column(db.Boolean, default=False)
    additional_info = db.Column(db.Text)
    
    def __repr__(self):
        return f'<BloodDonation {self.blood_group} by {self.donor.username}>'

# Blood Request model
class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    quantity_ml = db.Column(db.Integer)
    urgency_level = db.Column(db.String(20), default='normal')  # normal, urgent, critical
    status = db.Column(db.String(20), default='pending')  # pending, approved, fulfilled, unavailable
    date_requested = db.Column(db.DateTime, default=datetime.utcnow)
    matched_donation_id = db.Column(db.Integer, db.ForeignKey('blood_donation.id'))
    additional_info = db.Column(db.Text)
    
    # Relationship for matched donation
    matched_donation = db.relationship('BloodDonation', backref='matched_request', lazy=True, foreign_keys=[matched_donation_id])
    
    def __repr__(self):
        return f'<BloodRequest {self.blood_group} by {self.requester.username}>'

# OTP model for verification
class OTPVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)  # registration, donation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref='otps', lazy=True)
    
    def __repr__(self):
        return f'<OTPVerification for {self.user.username}>'
