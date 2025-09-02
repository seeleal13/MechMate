from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField, DateField, BooleanField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/user/Desktop/Mechmate/instance/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logs = db.relationship('RepairLog', backref='vehicle', lazy=True)

class RepairLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    mileage = db.Column(db.Integer)
    description = db.Column(db.Text, nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)

# Forms
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class VehicleForm(FlaskForm):
    make = SelectField('Make', choices=[], validators=[Optional()])
    custom_make = StringField('Custom Make', validators=[Optional()])
    use_custom_make = BooleanField('Use Custom Vehicle Details')
    model = SelectField('Model', choices=[('', 'Select Model')], validators=[Optional()])
    custom_model = StringField('Custom Model', validators=[Optional()])
    year = SelectField('Year', choices=[('', 'Select Year')], validators=[Optional()], coerce=lambda x: int(x) if x else None)
    custom_year = IntegerField('Custom Year', validators=[Optional()])
    license_plate = StringField('License Plate', validators=[DataRequired()])
    submit = SubmitField('Add Vehicle')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False
        if self.use_custom_make.data:
            if not self.custom_make.data:
                self.custom_make.errors.append('Custom Make is required if "Use Custom Vehicle Details" is checked.')
                return False
            if not self.custom_model.data:
                self.custom_model.errors.append('Custom Model is required if "Use Custom Vehicle Details" is checked.')
                return False
            if not self.custom_year.data:
                self.custom_year.errors.append('Custom Year is required if "Use Custom Vehicle Details" is checked.')
                return False
        else:
            if not self.make.data:
                self.make.errors.append('Make is required unless using custom vehicle details.')
                return False
            if not self.model.data:
                self.model.errors.append('Model is required unless using custom vehicle details.')
                return False
            if not self.year.data:
                self.year.errors.append('Year is required unless using custom vehicle details.')
                return False
        return True

class EditVehicleForm(FlaskForm):
    make = SelectField('Make', choices=[], validators=[Optional()])
    custom_make = StringField('Custom Make', validators=[Optional()])
    use_custom_make = BooleanField('Use Custom Vehicle Details')
    model = SelectField('Model', choices=[('', 'Select Model')], validators=[Optional()])
    custom_model = StringField('Custom Model', validators=[Optional()])
    year = SelectField('Year', choices=[('', 'Select Year')], validators=[Optional()], coerce=lambda x: int(x) if x else None)
    custom_year = IntegerField('Custom Year', validators=[Optional()])
    license_plate = StringField('License Plate', validators=[DataRequired()])
    submit = SubmitField('Update Vehicle')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False
        if self.use_custom_make.data:
            if not self.custom_make.data:
                self.custom_make.errors.append('Custom Make is required if "Use Custom Vehicle Details" is checked.')
                return False
            if not self.custom_model.data:
                self.custom_model.errors.append('Custom Model is required if "Use Custom Vehicle Details" is checked.')
                return False
            if not self.custom_year.data:
                self.custom_year.errors.append('Custom Year is required if "Use Custom Vehicle Details" is checked.')
                return False
        else:
            if not self.make.data:
                self.make.errors.append('Make is required unless using custom vehicle details.')
                return False
            if not self.model.data:
                self.model.errors.append('Model is required unless using custom vehicle details.')
                return False
            if not self.year.data:
                self.year.errors.append('Year is required unless using custom vehicle details.')
                return False
        return True

class LogForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    mileage = IntegerField('Mileage (Optional)', validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Log')

class EditLogForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    mileage = IntegerField('Mileage (Optional)', validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Update Log')

# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Static Car Data (Offline)
def get_car_makes():
    return [
        ('Ford', 'Ford'),
        ('Toyota', 'Toyota'),
        ('Honda', 'Honda'),
        ('Chevrolet', 'Chevrolet'),
        ('BMW', 'BMW'),
        ('Acura', 'Acura')
    ]

def get_car_models(make):
    models = {
        'Ford': [('F-150', 'F-150'), ('Mustang', 'Mustang'), ('Explorer', 'Explorer'), ('Escape', 'Escape')],
        'Toyota': [('Camry', 'Camry'), ('Corolla', 'Corolla'), ('RAV4', 'RAV4'), ('Highlander', 'Highlander')],
        'Honda': [('Civic', 'Civic'), ('Accord', 'Accord'), ('CR-V', 'CR-V'), ('Pilot', 'Pilot')],
        'Chevrolet': [('Silverado', 'Silverado'), ('Malibu', 'Malibu'), ('Equinox', 'Equinox'), ('Traverse', 'Traverse')],
        'BMW': [('3 Series', '3 Series'), ('X5', 'X5'), ('5 Series', '5 Series'), ('X3', 'X3')],
        'Acura': [('TLX', 'TLX'), ('MDX', 'MDX'), ('RDX', 'RDX'), ('ILX', 'ILX')]
    }
    return models.get(make, [('', 'Select Model')])

def get_car_years(make, model):
    return [(str(year), str(year)) for year in [2020, 2019, 2018, 2017]]

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    vehicles = current_user.vehicles
    return render_template('dashboard.html', vehicles=vehicles)

@app.route('/add_vehicle', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    form = VehicleForm()
    form.make.choices = get_car_makes()
    
    if request.method == 'POST':
        if form.make.data and not form.use_custom_make.data:
            form.model.choices = get_car_models(form.make.data)
            if form.model.data:
                form.year.choices = get_car_years(form.make.data, form.model.data)
        
        if form.validate_on_submit():
            try:
                vehicle = Vehicle(
                    make=form.custom_make.data if form.use_custom_make.data else form.make.data,
                    model=form.custom_model.data if form.use_custom_make.data else form.model.data,
                    year=form.custom_year.data if form.use_custom_make.data else form.year.data,
                    license_plate=form.license_plate.data,
                    owner_id=current_user.id
                )
                db.session.add(vehicle)
                db.session.commit()
                flash('Vehicle added successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding vehicle: {str(e)}', 'danger')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error in {field}: {error}', 'danger')
    
    if form.make.data and not form.use_custom_make.data:
        form.model.choices = get_car_models(form.make.data)
        if form.model.data:
            form.year.choices = get_car_years(form.make.data, form.model.data)
    else:
        form.model.choices = [('', 'Select Model')]
        form.year.choices = [('', 'Select Year')]
    
    return render_template('add_vehicle.html', form=form)

@app.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    form = EditVehicleForm()
    form.make.choices = get_car_makes()
    if request.method == 'POST':
        if form.make.data and not form.use_custom_make.data:
            form.model.choices = get_car_models(form.make.data)
            if form.model.data:
                form.year.choices = get_car_years(form.make.data, form.model.data)
        
        if form.validate_on_submit():
            try:
                vehicle.make = form.custom_make.data if form.use_custom_make.data else form.make.data
                vehicle.model = form.custom_model.data if form.use_custom_make.data else form.model.data
                vehicle.year = form.custom_year.data if form.use_custom_make.data else form.year.data
                vehicle.license_plate = form.license_plate.data
                db.session.commit()
                flash('Vehicle updated successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating vehicle: {str(e)}', 'danger')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error in {field}: {error}', 'danger')
    
    if request.method == 'GET':
        form.make.data = vehicle.make
        form.custom_make.data = vehicle.make if vehicle.make not in [make[0] for make in get_car_makes()] else ''
        form.use_custom_make.data = vehicle.make not in [make[0] for make in get_car_makes()]
        form.model.data = vehicle.model
        form.custom_model.data = vehicle.model if vehicle.model not in [model[0] for model in get_car_models(vehicle.make)] else ''
        form.year.data = str(vehicle.year)
        form.custom_year.data = vehicle.year if str(vehicle.year) not in [str(year) for year in [2020, 2019, 2018, 2017]] else None
        form.license_plate.data = vehicle.license_plate
        form.model.choices = get_car_models(vehicle.make)
        form.year.choices = get_car_years(vehicle.make, vehicle.model)
    
    return render_template('edit_vehicle.html', form=form, vehicle=vehicle)

@app.route('/delete_vehicle/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        db.session.delete(vehicle)
        db.session.commit()
        flash('Vehicle deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting vehicle: {str(e)}', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/api/models/<make>')
@login_required
def get_models(make):
    models = get_car_models(make)
    return jsonify(models)

@app.route('/api/years/<make>/<model>')
@login_required
def get_years(make, model):
    years = get_car_years(make, model)
    return jsonify(years)

@app.route('/vehicle/<int:vehicle_id>/add_log', methods=['GET', 'POST'])
@login_required
def add_log(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id:
        flash('Not your vehicle.', 'danger')
        return redirect(url_for('dashboard'))
    form = LogForm()
    if form.validate_on_submit():
        try:
            log = RepairLog(
                date=form.date.data,
                mileage=form.mileage.data,
                description=form.description.data,
                vehicle_id=vehicle_id
            )
            db.session.add(log)
            db.session.commit()
            flash('Log added successfully!', 'success')
            return redirect(url_for('view_logs', vehicle_id=vehicle_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding log: {str(e)}', 'danger')
    return render_template('add_log.html', form=form, vehicle=vehicle)

@app.route('/vehicle/<int:vehicle_id>/edit_log/<int:log_id>', methods=['GET', 'POST'])
@login_required
def edit_log(vehicle_id, log_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    log = RepairLog.query.get_or_404(log_id)
    if vehicle.owner_id != current_user.id or log.vehicle_id != vehicle_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    form = EditLogForm()
    if form.validate_on_submit():
        try:
            log.date = form.date.data
            log.mileage = form.mileage.data
            log.description = form.description.data
            db.session.commit()
            flash('Log updated successfully!', 'success')
            return redirect(url_for('view_logs', vehicle_id=vehicle_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating log: {str(e)}', 'danger')
    elif request.method == 'GET':
        form.date.data = log.date
        form.mileage.data = log.mileage
        form.description.data = log.description
    return render_template('edit_log.html', form=form, vehicle=vehicle, log=log)

@app.route('/vehicle/<int:vehicle_id>/delete_log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(vehicle_id, log_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    log = RepairLog.query.get_or_404(log_id)
    if vehicle.owner_id != current_user.id or log.vehicle_id != vehicle_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    try:
        db.session.delete(log)
        db.session.commit()
        flash('Log deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting log: {str(e)}', 'danger')
    return redirect(url_for('view_logs', vehicle_id=vehicle_id))

@app.route('/vehicle/<int:vehicle_id>/logs')
@login_required
def view_logs(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id:
        flash('Not your vehicle.', 'danger')
        return redirect(url_for('dashboard'))
    logs = RepairLog.query.filter_by(vehicle_id=vehicle_id).order_by(RepairLog.date.desc()).all()
    return render_template('view_logs.html', vehicle=vehicle, logs=logs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)