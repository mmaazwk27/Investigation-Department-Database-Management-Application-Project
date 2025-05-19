from app import db
from datetime import datetime
from flask_login import UserMixin
from datetime import date



# User Model
class User(db.Model, UserMixin):  # UserMixin helps manage login sessions
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # either 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Criminal Table
class Criminal(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    criminal_type = db.Column(db.String(50), nullable=False)   # Convicted, Repeat Offender, Accomplice 
    crime_committed = db.Column(db.String(255), nullable=False)
    arrest_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False)  # Arrested, Wanted, Released
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

# Crime Table
class Crime(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    crime_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    police_station_id = db.Column(db.String(10), db.ForeignKey('police_station.id'))
    criminal_id = db.Column(db.String(10), db.ForeignKey('criminal.id'))
    victims = db.relationship('Victim', back_populates='crime', cascade='all, delete-orphan')
    witnesses = db.relationship('Witness', back_populates='crime', cascade='all, delete-orphan')
    evidences = db.relationship('Evidence', back_populates='crime', cascade='all, delete-orphan')

    
# Police Officer Table
class PoliceOfficer(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rank = db.Column(db.String(50), nullable=False)
    badge_number = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    police_station_id = db.Column(db.String(10), db.ForeignKey('police_station.id'))

# Police Station Table
class PoliceStation(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    officers = db.relationship('PoliceOfficer', backref='station', lazy=True)


# Case Table (Manages Criminal Cases)
class Cases(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    crime_id = db.Column(db.String(10), db.ForeignKey('crime.id'))
    police_officer_id = db.Column(db.String(10), db.ForeignKey('police_officer.id'))
    status = db.Column(db.String(50), nullable=False)  # Open, Closed, Under Investigation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Victim Table
class Victim(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    crime_id = db.Column(db.String(10), db.ForeignKey('crime.id'))
    crime = db.relationship('Crime', back_populates='victims')

    
    def calculate_age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

# Witness Table
class Witness(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    statement = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    crime_id = db.Column(db.String(10), db.ForeignKey('crime.id'))
    crime = db.relationship('Crime', back_populates='witnesses')



# Evidence Table
class Evidence(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    crime_id = db.Column(db.String(10), db.ForeignKey('crime.id'))
    police_officer_id = db.Column(db.String(10), db.ForeignKey('police_officer.id'))
    submission_date = db.Column(db.Date, default=datetime.utcnow)
    crime = db.relationship('Crime', back_populates='evidences')


    
