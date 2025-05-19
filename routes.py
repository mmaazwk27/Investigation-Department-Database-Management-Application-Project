from flask import render_template, redirect, url_for, flash, request, abort
from app import app, db
from models import *
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from flask_wtf.csrf import CSRFError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload




# ===========================
# ADMIN PROTECTION FOR ROUTES
# ===========================

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# ===========================
# ERROR PAGE ROUTE
# ===========================

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Your session has expired or is invalid. Please try again.', 'warning')
    return redirect(url_for('index'))

@app.errorhandler(IntegrityError)
def handle_integrity_error(e):
    db.session.rollback()  # rollback the failed transaction
    error_msg = str(e.orig).lower()

    if 'duplicate' in error_msg or 'unique constraint' in error_msg:
        flash('Error: Duplicate entry detected. Please use unique values.', 'danger')
    else:
        flash('A database error occurred. Please try again.', 'danger')
    
    return redirect(request.referrer or url_for('index'))


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect users to login if not authenticated

# User Loader (Required for Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------ AUTHENTICATION ROUTES ------------------


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Redirect to the main dashboard if logged in
    return render_template('home.html')  # Show login/register options if not logged in


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Redirect already logged-in users
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)  # Log in the user
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to main page
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Redirect already logged-in users
    
    form = RegisterForm()
    if form.validate_on_submit():  # Ensure form validation is working
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You may now log in.', 'success')
            return redirect(url_for('home'))  # Redirect to home page after registration
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
    
    return render_template('register.html', form=form)


@app.route("/register_admin", methods=['GET', 'POST'])
def register_admin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        admin = User(username=form.username.data,
                     email=form.email.data,
                     password=hashed_password,
                     role='admin')
        try:
            db.session.add(admin)
            db.session.commit()
            flash('Admin account created successfully! You may now log in.', 'success')
            return redirect(url_for('home'))  # Redirect to home page after registration
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
    return render_template('register_admin.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))  # Redirect to login after logout

# ------------------ END AUTHENTICATION ROUTES ------------------


## ================================
## dashboard Route
## ================================

@app.route('/index')  # Main page after login
@login_required
def index():
    total_stations = PoliceStation.query.count()
    total_officers = PoliceOfficer.query.count()
    total_crimes = Crime.query.count()
    total_cases = Cases.query.count()
    total_users = User.query.count()
    return render_template('index.html',
                           total_stations=total_stations,
                           total_officers=total_officers,
                           total_crimes=total_crimes,
                           total_cases=total_cases,
                           total_users=total_users) 




# ================================
# Accounts Routes
# ================================


@app.route('/user_accounts')
@login_required
@admin_required
def view_accounts():
    csrf_form=CSRFOnlyForm()
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('view_accounts.html', users=users, csrf_form=csrf_form)

@app.route('/user_accounts/edit_user_role/<user_id>', methods=['POST'])
@login_required
@admin_required
def edit_user_role(user_id):
    form = CSRFOnlyForm()
    if form.validate_on_submit():
        if current_user.role != 'admin':
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('view_accounts'))

        user = User.query.get_or_404(user_id)
        new_role = request.form['role']
        security_key = request.form.get('security_key')
        expected = current_app.config['ADMIN_SECURITY_KEY']

        if security_key != expected:
            flash('Invalid security key. Role not updated.', 'danger')
            return redirect(url_for('view_accounts'))
        
        if user.id == current_user.id and new_role != current_user.role:
            flash("You cannot change your own role while logged in.", "danger")
            return redirect(url_for('view_accounts'))

        user.role = new_role
        db.session.commit()
        flash('Account Role updated successfully', 'success')
    else:
        flash('Invalid or missing CSRF token.', 'danger')

    return redirect(url_for('view_accounts'))




@app.route('/user_accounts/delete/<user_id>', methods=['POST'])
@login_required
@admin_required
def delete_account(user_id):
    if current_user.role != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('view_accounts'))

    user = User.query.get_or_404(user_id)
    key = request.form.get("security_key")
    expected = current_app.config['ADMIN_SECURITY_KEY']

    if key != expected:  
        flash("Invalid security key.", "danger")
        return redirect(url_for('view_accounts'))

    db.session.delete(user)
    db.session.commit()
    flash(f'Account {user_id} deleted successfully.', 'danger')
    return redirect(request.referrer or url_for('view_accounts'))



# ================================
# Crimes Routes
# ================================
@app.route('/crimes')
@login_required
def view_crimes():
    crimes = Crime.query.options(
        joinedload(Crime.victims),
        joinedload(Crime.witnesses),
        joinedload(Crime.evidences),
    ).order_by(Crime.date.desc()).all()
    return render_template('view_crimes.html', crimes=crimes)

@app.route('/crimes/<string:crime_id>')
@login_required
def crime_details(crime_id):
    crime = Crime.query.get_or_404(crime_id)

     # Fetch related entries
    witness = crime.witnesses if hasattr(crime, 'witnesses') else []
    evidence = crime.evidences if hasattr(crime, 'evidences') else []
    victim = crime.victims if hasattr(crime, 'victims') else []


    return render_template('view_entity.html', title='Crime Details', entity=crime, related_data={
            'witnesses': witness,
            'evidences': evidence,
            'victims': victim
        })

@app.route('/crime/add', methods=['GET', 'POST'])
@login_required
@admin_required

def add_crime():
    form = CrimeForm()
    stations = PoliceStation.query.order_by(PoliceStation.name).all()
    form.police_station_id.choices = [(s.id, s.name) for s in stations]
    criminals = Criminal.query.order_by(Criminal.name).all()
    form.criminal_id.choices = [(s.id, f'{s.id} - {s.name}') for s in criminals]

    if form.validate_on_submit():  # Check if the form is submitted and valid
        new_crime = Crime(
            id=form.id.data,
            crime_type=form.crime_type.data,
            location=form.location.data,
            date=form.date.data,
            description=form.description.data,
            police_station_id=form.police_station_id.data,
            criminal_id=form.criminal_id.data
        )
        db.session.add(new_crime)
        db.session.commit()  # Save to database

        flash("Crime added successfully!", "success")
        return redirect(url_for('view_crimes'))  # Redirect to the crimes list

    return render_template("add_crime.html", form=form)



@app.route('/crime/delete/<string:crime_id>')
@login_required
@admin_required
def delete_crime(crime_id):
    crime = Crime.query.get_or_404(crime_id)
    try:
        db.session.delete(crime)
        db.session.commit()
        flash(f'Crime {crime_id} deleted successfully.', 'danger')
    except IntegrityError:
        db.session.rollback()
        flash(f'Cannot delete: this crime {crime_id} is connected to other records.', 'warning')
    return redirect(request.referrer or url_for('view_crimes'))

# ================================
# Criminals Routes
# ================================
@app.route('/criminals')
@login_required
def view_criminals():
    criminals = Criminal.query.order_by(Criminal.created_at.desc()).all()
    csrf_form=CSRFOnlyForm()
    return render_template('view_criminals.html', criminals=criminals, csrf_form=csrf_form)

@app.route('/criminals/<string:criminal_id>')
@login_required
def criminal_details(criminal_id):
    criminal = Criminal.query.get_or_404(criminal_id)
    return render_template('view_entity.html', title='Criminal Details', entity=criminal)


@app.route('/criminal/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_criminal():
    form = CriminalForm()
    if form.validate_on_submit():
        new_criminal = Criminal(
            id=form.id.data,
            name=form.name.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            criminal_type=form.criminal_type.data,
            crime_committed=form.crime_committed.data,
            arrest_date=form.arrest_date.data,
            status=form.status.data,
        )
        db.session.add(new_criminal)
        db.session.commit()
        flash('Criminal added successfully!', 'success')
        return redirect(url_for('view_criminals'))
    return render_template('add_criminal.html', form=form)


@app.route('/criminal/edit_criminal_status/<string:criminal_id>', methods=['POST'])
@login_required
@admin_required
def edit_criminal_status(criminal_id):
    form = CSRFOnlyForm()

    if form.validate_on_submit():
        criminal = Criminal.query.get_or_404(criminal_id)
        new_status = request.form['criminal_status']
        criminal.status = new_status
        db.session.commit()
        flash('Criminal status updated successfully', 'success')
    else:
        flash('Invalid or missing CSRF token.', 'danger')

    return redirect(url_for('view_criminals'))

@app.route('/criminal/delete/<string:criminal_id>')
@login_required
@admin_required
def delete_criminal(criminal_id):
    criminal = Criminal.query.get_or_404(criminal_id)
    try:
        db.session.delete(criminal)
        db.session.commit()
        flash(f'Criminal {criminal_id} deleted successfully.', 'danger')
    except IntegrityError:
        db.session.rollback()
        flash(f'Cannot delete criminal {criminal_id}: it is referenced by other records.', 'warning')
    return redirect(request.referrer or url_for('view_criminals'))

# ================================
# Police Officers Routes
# ================================
@app.route('/police_officers')
@login_required
def view_police_officers():
    officers = PoliceOfficer.query.order_by(PoliceOfficer.created_at.desc()).all()
    return render_template('view_police_officers.html', police_officer=officers)

@app.route('/police_officers/<string:police_officer_id>')
@login_required
def police_officer_details(police_officer_id):
    officer = PoliceOfficer.query.get_or_404(police_officer_id)
    return render_template('view_entity.html', title='Police Officer Details', entity=officer)


@app.route('/police_officer/add',methods=['GET','POST'])
@login_required
@admin_required
def add_officer():
    form = PoliceOfficerForm()
    station = PoliceStation.query.order_by(PoliceStation.name).all()
    form.police_station_id.choices = [(p.id,p.name)for p in station]
    
    if form.validate_on_submit():
        new_officer = PoliceOfficer(
            id = form.id.data,
            name = form.name.data,
            rank = form.rank.data,
            badge_number = form.badge_number.data,
            police_station_id=form.police_station_id.data,
        )
        db.session.add(new_officer)
        db.session.commit()
        flash('Police Officer Added Succesfully!','success')
        return redirect(url_for('view_police_officers'))
    return render_template('add_officer.html',form = form)

@app.route('/police_officer/delete/<string:officer_id>')
@login_required
@admin_required
def delete_police_officer(officer_id):
    officer = PoliceOfficer.query.get_or_404(officer_id)
    try:
        db.session.delete(officer)
        db.session.commit()
        flash(f'Police officer {officer_id} deleted.', 'danger')
    except IntegrityError:
        db.session.rollback()
        flash(f'Cannot delete: police officer {officer_id} is referenced in other records.', 'warning')
    return redirect(request.referrer or url_for('view_police_officers'))

# ================================
# Police Stations Routes
# ================================
@app.route('/police_station')
@login_required
def view_police_stations():
    stations = PoliceStation.query.order_by(PoliceStation.created_at.desc()).all()
    return render_template('view_police_stations.html', police_station=stations)


@app.route('/police_stations/<string:police_station_id>')
@login_required
def police_station_details(police_station_id):
    entity = PoliceStation.query.get_or_404(police_station_id)
    return render_template('view_entity.html',
                           title='Police Station Details',
                           entity=entity)



@app.route('/police_station/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_police_station():
    form = PoliceStationForm()
    if form.validate_on_submit():
        station = PoliceStation(
            id=form.id.data,
            name=form.name.data,
            location=form.location.data
        )
        db.session.add(station)
        db.session.commit()
        flash('Police Station added successfully!', 'success')
        return redirect(url_for('view_police_stations'))
    return render_template('add_police_station.html', form=form)

@app.route('/police_station/delete/<string:station_id>')
@login_required
@admin_required
def delete_police_station(station_id):
    station = PoliceStation.query.get_or_404(station_id)
    try:
        db.session.delete(station)
        db.session.commit()
        flash(f'Police station {station_id} deleted.', 'danger')
    except IntegrityError:
        db.session.rollback()
        flash(f'Cannot delete: police station {station_id} is referenced in other records.', 'warning')
    return redirect(request.referrer or url_for('view_police_stations'))

# ================================
# Search Routes
# ================================

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    results = Crime.query.filter(Crime.crime_type.ilike(f"%{query}%")).all()
    return render_template('view_crimes.html', crimes=results, search_query=query)

# ================================
# Case Routes
# ================================

@app.route('/case')
@login_required
def view_case():
    cases = Cases.query.order_by(Cases.created_at.desc()).all()
    csrf_form=CSRFOnlyForm()
    return render_template('view_cases.html', cases = cases, csrf_form=csrf_form)    


@app.route('/case/<string:case_id>')
@login_required
def case_details(case_id):
    case = Cases.query.get_or_404(case_id)
    return render_template('view_entity.html', title='Case Details', entity=case)

@app.route('/case/add',methods=['GET','POST'])
@login_required
@admin_required
def add_case():
    form = CaseForm()
    crimes = Crime.query.order_by(Crime.id).all()
    form.crime_id.choices = [(c.id,c.id)for c in crimes]
    officers = PoliceOfficer.query.order_by(PoliceOfficer.name).all()
    form.police_officer_id.choices = [(p.id,p.name)for p in officers]
    
    if form.validate_on_submit():
        new_case = Cases(
            id = form.id.data,
            crime_id = form.crime_id.data,
            police_officer_id = form.police_officer_id.data,
            status = form.status.data,
        )
        db.session.add(new_case)
        db.session.commit()
        flash('Case Added Succesfully!','success')
        return redirect(url_for('view_case'))
    return render_template('add_case.html',form = form)

@app.route('/case/delete/<string:case_id>')
@login_required
@admin_required
def delete_case(case_id):
    case = Cases.query.get_or_404(case_id)
    try:
        db.session.delete(case)
        db.session.commit()
        flash(f'Case {case_id} deleted successfully!', 'danger')
    except IntegrityError:
        db.session.rollback()
        flash(f'Cannot delete: this case {case_id} is linked with other entities.', 'warning')
    return redirect(request.referrer or url_for('view_cases'))

@app.route('/case/edit_case_status/<string:case_id>',methods = ['POST'])
@login_required
@admin_required
def edit_case_status(case_id):
    form = CSRFOnlyForm()

    if form.validate_on_submit():
        case = Cases.query.get_or_404(case_id)
        new_status = request.form['case_status']
        case.status = new_status
        db.session.commit()
        flash('Case status updated successfully', 'success')
    else:
        flash('Invalid or missing CSRF token.', 'danger')

    return redirect(url_for('view_case'))


# ================================
#  Evidence Routes
# ================================

@app.route('/evidence')
@login_required
def view_evidence():
    evidences = Evidence.query.order_by(Evidence.submission_date.desc()).all()
    return render_template('view_evidence.html',evidences = evidences)


@app.route('/evidence/<string:evidence_id>')
@login_required
def evidence_details(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    return render_template('view_entity.html', title='Evidence Details', entity=evidence)

@app.route('/evidence/add',methods=['GET','POST'])
@login_required
@admin_required
def add_evidence():
    form = EvidenceForm()
    crimes = Crime.query.order_by(Crime.id).all()
    form.crime_id.choices = [(c.id,c.id)for c in crimes]
    officers = PoliceOfficer.query.order_by(PoliceOfficer.name).all()
    form.police_officer_id.choices = [(p.id,p.name)for p in officers]
    
    if form.validate_on_submit():
        new_evidence = Evidence(
            id = form.id.data,
            description = form.description.data,
            crime_id = form.crime_id.data,
            police_officer_id = form.police_officer_id.data,
            submission_date = form.submission_date.data,
        )
        db.session.add(new_evidence)
        db.session.commit()
        flash('Evidence Added Succesfully!','success')
        return redirect(url_for('view_evidence'))
    return render_template('add_evidence.html',form = form)

@app.route('/evidence/delete/<string:evidence_id>')
@login_required
@admin_required
def delete_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    try:
        db.session.delete(evidence)
        db.session.commit()
        flash(f'Evidence {evidence_id} deleted.', 'danger')
    except IntegrityError:
        db.session.rollback()
        flash(f'Cannot delete: evidence {evidence_id} is referenced elsewhere.', 'warning')
    return redirect(request.referrer or url_for('view_evidence'))


# ================================
#  Witness Routes
# ================================

@app.route('/witness')
@login_required
def view_witness():
    witness = Witness.query.order_by(Witness.created_at.desc()).all()
    return render_template('view_witness.html',witnesses = witness)

@app.route('/witness/<string:witness_id>')
@login_required
def witness_details(witness_id):
    witness = Witness.query.get_or_404(witness_id)
    return render_template('view_entity.html', title='Witness Details', entity=witness)


@app.route('/witness/add',methods=['GET','POST'])
@login_required
@admin_required
def add_witness():
    form = WitnessForm()
    crime = Crime.query.order_by(Crime.id).all()
    form.crime_id.choices = [(c.id,c.id)for c in crime]
    
    if form.validate_on_submit():
        new_witness = Witness(
            id = form.id.data,
            name = form.name.data,
            statement = form.statement.data,
            crime_id = form.crime_id.data,
        )
        db.session.add(new_witness)
        db.session.commit()
        flash('Witness Added Succesfully!','success')
        return redirect(url_for('view_witness'))
    return render_template('add_witness.html',form = form)

@app.route('/witness/delete/<string:witness_id>')
@login_required
@admin_required
def delete_witness(witness_id):
    witness = Witness.query.get_or_404(witness_id)
    try:
        db.session.delete(witness)
        db.session.commit()
        flash(f'Witness {witness_id} deleted.', 'danger')
    except IntegrityError:
        db.session.rollback()
        flash(f'Cannot delete: witness {witness_id} is referenced elsewhere.', 'warning')
    return redirect(request.referrer or url_for('view_witness'))

# ================================
#  Victim Routes
# ================================

@app.route('/victim')
@login_required
def view_victim():
    victim = Victim.query.order_by(Victim.created_at.desc()).all()
    return render_template('view_victim.html',victims = victim)

@app.route('/victim/<string:victim_id>')
@login_required
def victim_details(victim_id):
    victim = Victim.query.get_or_404(victim_id)
    return render_template('view_entity.html', title='Victim Details', entity=victim)

@app.route('/victim/add',methods=['GET','POST'])
@login_required
@admin_required
def add_victim():
    form = VictimForm()
    crime = Crime.query.order_by(Crime.id).all()
    form.crime_id.choices = [(c.id,c.id)for c in crime]
    
    if form.validate_on_submit():
        new_victim = Victim(
            id = form.id.data,
            name = form.name.data,
            date_of_birth = form.date_of_birth.data,
            gender = form.gender.data,
            crime_id = form.crime_id.data,
        )
        db.session.add(new_victim)
        db.session.commit()
        flash(f'Victim Added Succesfully!','success')
        return redirect(url_for('view_victim'))
    return render_template('add_victim.html',form = form)

@app.route('/victim/delete/<string:victim_id>')
@login_required
@admin_required
def delete_victim(victim_id):
    victim = Victim.query.get_or_404(victim_id)
    try:
        db.session.delete(victim)
        db.session.commit()
        flash(f'Victim {victim_id} deleted.', 'danger')
    except IntegrityError:
        db.session.rollback()
        flash(f'Cannot delete: victim {victim_id} is referenced elsewhere.', 'warning')
    return redirect(request.referrer or url_for('view_victim'))


