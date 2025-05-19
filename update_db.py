from app import app, db
from models import *
from sqlalchemy import text

# Run this script to update the database schema with new columns
if __name__ == "__main__":
    with app.app_context():
        # Use alter table statements to add the new columns
        try:
            print("Adding new columns to organ_donation table...")
            
            # Organ donation table updates
            db.session.execute(text('ALTER TABLE organ_donation ADD COLUMN IF NOT EXISTS donor_age INTEGER'))
            db.session.execute(text('ALTER TABLE organ_donation ADD COLUMN IF NOT EXISTS hla_type VARCHAR(50)'))
            db.session.execute(text('ALTER TABLE organ_donation ADD COLUMN IF NOT EXISTS tissue_crossmatch VARCHAR(20)'))
            db.session.execute(text('ALTER TABLE organ_donation ADD COLUMN IF NOT EXISTS location_lat FLOAT'))
            db.session.execute(text('ALTER TABLE organ_donation ADD COLUMN IF NOT EXISTS location_lng FLOAT'))
            db.session.execute(text('ALTER TABLE organ_donation ADD COLUMN IF NOT EXISTS is_living_donor BOOLEAN DEFAULT FALSE'))
            db.session.execute(text('ALTER TABLE organ_donation ADD COLUMN IF NOT EXISTS medical_condition VARCHAR(100)'))
            
            print("Adding new columns to organ_request table...")
            
            # Organ request table updates
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS patient_age INTEGER'))
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS hla_type VARCHAR(50)'))
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS weight_kg FLOAT'))
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS height_cm FLOAT'))
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS medical_urgency_score INTEGER'))
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS waiting_time_days INTEGER'))
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS previous_transplants INTEGER DEFAULT 0'))
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS location_lat FLOAT'))
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS location_lng FLOAT'))
            db.session.execute(text('ALTER TABLE organ_request ADD COLUMN IF NOT EXISTS medical_condition VARCHAR(100)'))
            
            # Commit the transaction
            db.session.commit()
            
            print("Database schema updated successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating database schema: {str(e)}")