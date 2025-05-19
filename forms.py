from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,DateField, SubmitField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User
from flask import flash, current_app
import re


class CSRFOnlyForm(FlaskForm):
    pass

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):

    def validate_strong_password(self, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must include at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must include at least one special character.')
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('Password must include at least one letter.')
        

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                             validators=[DataRequired(),validate_strong_password ])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password', message="Passwords must match!")])
    submit = SubmitField('Register')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is already taken. Please choose another one.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("An account with this email already exists. Please use another one.")


class AdminRegistrationForm(RegisterForm):
    security_key = PasswordField('Security Key', validators=[DataRequired(), Length(min=6)])

    def validate_security_key(self, field):
        expected = current_app.config['ADMIN_SECURITY_KEY']
        if field.data != expected:
            raise ValidationError('Invalid security key. You are not authorized to register an admin.')


class CriminalForm(FlaskForm):
    id = StringField("Criminal ID", validators=[DataRequired(), Length(max=10)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])    
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    criminal_type=SelectField('Criminal Type', choices=[('Convicted', 'Convicted'), ('Repeat Offender', 'Repeat Offender'), ('Accomplice', 'Accomplice')], validators=[DataRequired()])
    crime_committed = TextAreaField('Crime Committed', validators=[DataRequired(), Length(max=255)])
    arrest_date = DateField('Arrest Date', format='%Y-%m-%d',validators=[])
    status = SelectField('Status', choices=[('Arrested', 'Arrested'), ('Wanted', 'Wanted'), ('Released', 'Released')], validators=[DataRequired()])
    submit = SubmitField('Submit')

            
    def validate_date_of_birth(self, field):
        from datetime import date
        today = date.today()
        age = (today - field.data).days // 365
        if age < 10:
            flash('Criminal must be at least 10 years old.','danger')
            raise ValidationError('Criminal must be at least 10 years old.')

    def validate_arrest_date(self, field):
        from datetime import timedelta
        # Only enforce when status is Arrested or Released
        if self.status.data in ('Arrested', 'Released'):
            if not field.data:
                flash('Arrest date is required when status is Arrested or Released.','danger')
                raise ValidationError('Arrest date is required when status is Arrested or Released.')
            tenth_bday = self.date_of_birth.data + timedelta(days=10*365)
            if field.data <= tenth_bday:
                flash('Invalid Arrest Date! Criminal must be at least 10 years old','danger')
                raise ValidationError('Arrest date must be after the 10th birthday.')
            if field.data <= self.date_of_birth.data:
                flash('Arrest date must be after date of birth.','danger')
                raise ValidationError('Arrest date must be after date of birth.')
        else:
            # Prevent an arrest_date sneak‑in when not arrested/released
            if field.data:
                raise ValidationError('Cannot specify an arrest date unless status is Arrested or Released.')

    

# Crime Form
class CrimeForm(FlaskForm):
    id = StringField("Crime ID", validators=[DataRequired(), Length(max=10)])
    crime_type = StringField("Crime Type", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired()])  # Fix: Add this field
    description = TextAreaField("Description")
    police_station_id = SelectField('Police Station ID', validators=[DataRequired()])
    criminal_id = SelectField('Criminal ID', validators=[DataRequired()])
    submit = SubmitField("Add Crime")


# Police Officer Form
class PoliceOfficerForm(FlaskForm):
    id = StringField(" ID", validators=[DataRequired(), Length(max=10)])
    name = StringField('Officer Name', validators=[DataRequired(), Length(max=100)])
    rank = StringField('Rank', validators=[DataRequired(), Length(max=50)])
    badge_number = StringField('Badge Number', validators=[DataRequired(), Length(max=50)])
    police_station_id = SelectField('Assigned Station ID', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Police Station Form
class PoliceStationForm(FlaskForm):
    id = StringField("Police Station ID", validators=[DataRequired(), Length(max=10)])
    name = StringField('Station Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Submit')

# ===========================
# Case Management Forms
# ===========================

# Case Form
class CaseForm(FlaskForm):
    id = StringField("Case ID", validators=[DataRequired(), Length(max=10)])
    crime_id = SelectField('Crime ID', validators=[DataRequired()])
    police_officer_id = SelectField('Police Officer ID', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Open', 'Open'), ('Closed', 'Closed'), ('Under Investigation', 'Under Investigation')], validators=[DataRequired()])
    submit = SubmitField('Submit')

# ================================
# Victim, Witness & Evidence Forms
# =================================

# Victim Form
class VictimForm(FlaskForm):
    id = StringField("Victim ID", validators=[DataRequired(), Length(max=10)])
    name = StringField('Victim Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])    
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    crime_id = SelectField('Crime ID', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Witness Form
class WitnessForm(FlaskForm):
    id = StringField("Witness ID", validators=[DataRequired(), Length(max=10)])
    name = StringField('Witness Name', validators=[DataRequired(), Length(max=100)])
    statement = TextAreaField('Statement', validators=[DataRequired()])
    crime_id = SelectField('Crime ID', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Evidence Form
class EvidenceForm(FlaskForm):
    id = StringField("Evidence ID", validators=[DataRequired(), Length(max=10)])
    description = TextAreaField('Evidence Description', validators=[DataRequired(), Length(max=255)])
    crime_id = SelectField('Crime ID', validators=[DataRequired()])
    police_officer_id = SelectField('Submitted by Officer ID', validators=[DataRequired()])
    submission_date = DateField('Submission Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Submit')


