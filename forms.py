from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField, IntegerField, HiddenField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from models import User

# Authentication Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another one or login.')

class OTPVerificationForm(FlaskForm):
    otp = StringField('Enter OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')

# User Forms
class OrganDonationForm(FlaskForm):
    organ_type = SelectField('Organ Type', choices=[
        ('kidney', 'Kidney'),
        ('liver', 'Liver'),
        ('heart', 'Heart'),
        ('lungs', 'Lungs'),
        ('pancreas', 'Pancreas'),
        ('cornea', 'Cornea')
    ], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], validators=[DataRequired()])
    # Advanced matching criteria
    donor_age = IntegerField('Donor Age', validators=[Optional(), NumberRange(min=18, max=120)])
    hla_type = SelectField('HLA Type', choices=[
        ('', 'Unknown'),
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B7', 'B7'),
        ('B8', 'B8'),
        ('DR1', 'DR1'),
        ('DR2', 'DR2')
    ], validators=[Optional()])
    tissue_crossmatch = SelectField('Tissue Crossmatch', choices=[
        ('', 'Unknown'),
        ('positive', 'Positive'),
        ('negative', 'Negative')
    ], validators=[Optional()])
    location_lat = FloatField('Location Latitude', validators=[Optional()])
    location_lng = FloatField('Location Longitude', validators=[Optional()])
    is_living_donor = BooleanField('Living Donor', default=False)
    medical_condition = StringField('Medical Condition', validators=[Optional(), Length(max=100)])
    additional_info = TextAreaField('Additional Information', validators=[Optional()])
    submit = SubmitField('Donate Organ')

class OrganRequestForm(FlaskForm):
    organ_type = SelectField('Organ Type', choices=[
        ('kidney', 'Kidney'),
        ('liver', 'Liver'),
        ('heart', 'Heart'),
        ('lungs', 'Lungs'),
        ('pancreas', 'Pancreas'),
        ('cornea', 'Cornea')
    ], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], validators=[DataRequired()])
    urgency_level = SelectField('Urgency Level', choices=[
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical')
    ], validators=[DataRequired()])
    # Advanced matching criteria
    patient_age = IntegerField('Patient Age', validators=[Optional(), NumberRange(min=0, max=120)])
    hla_type = SelectField('HLA Type', choices=[
        ('', 'Unknown'),
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B7', 'B7'),
        ('B8', 'B8'),
        ('DR1', 'DR1'),
        ('DR2', 'DR2')
    ], validators=[Optional()])
    weight_kg = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=0, max=500)])
    height_cm = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=0, max=300)])
    medical_urgency_score = IntegerField('Medical Urgency Score (1-100)', validators=[Optional(), NumberRange(min=1, max=100)])
    waiting_time_days = IntegerField('Days on Waiting List', validators=[Optional(), NumberRange(min=0)])
    previous_transplants = IntegerField('Previous Transplants', validators=[Optional(), NumberRange(min=0)])
    location_lat = FloatField('Location Latitude', validators=[Optional()])
    location_lng = FloatField('Location Longitude', validators=[Optional()])
    medical_condition = StringField('Medical Condition', validators=[Optional(), Length(max=100)])
    additional_info = TextAreaField('Additional Information', validators=[Optional()])
    submit = SubmitField('Request Organ')

class BloodDonationForm(FlaskForm):
    blood_group = SelectField('Blood Group', choices=[
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], validators=[DataRequired()])
    quantity_ml = IntegerField('Quantity (ml)', validators=[DataRequired()])
    additional_info = TextAreaField('Additional Information', validators=[Optional()])
    submit = SubmitField('Donate Blood')

class BloodRequestForm(FlaskForm):
    blood_group = SelectField('Blood Group', choices=[
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], validators=[DataRequired()])
    quantity_ml = IntegerField('Quantity (ml)', validators=[DataRequired()])
    urgency_level = SelectField('Urgency Level', choices=[
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical')
    ], validators=[DataRequired()])
    additional_info = TextAreaField('Additional Information', validators=[Optional()])
    submit = SubmitField('Request Blood')

class ProfileUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

# Admin Forms
class DoctorForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    specialization = StringField('Specialization', validators=[DataRequired()])
    license_number = StringField('License Number', validators=[DataRequired()])
    hospital = SelectField('Hospital', coerce=int, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add Doctor')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another one.')

class HospitalForm(FlaskForm):
    name = StringField('Hospital Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Add Hospital')

class AssignDoctorForm(FlaskForm):
    doctor = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Doctor')

class UpdateRequestStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('unavailable', 'Unavailable'),
        ('fulfilled', 'Fulfilled')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')

class OTPCollectionForm(FlaskForm):
    otp = StringField('Enter OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify & Collect')
