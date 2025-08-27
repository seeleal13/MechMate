from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField
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
    date = db.Column(db.DateTime, default=datetime.utcnow)
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
    make = SelectField('Make', choices=[], validators=[DataRequired()])
    model = SelectField('Model', choices=[('', 'Select Model')], validators=[DataRequired()])
    year = SelectField('Year', choices=[('', 'Select Year')], validators=[DataRequired()], coerce=lambda x: int(x) if x else None)
    license_plate = StringField('License Plate', validators=[DataRequired()])
    submit = SubmitField('Add Vehicle')

class LogForm(FlaskForm):
    mileage = IntegerField('Mileage (Optional)', validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Log')

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
        # Update choices based on submitted data before validation
        if form.make.data:
            form.model.choices = get_car_models(form.make.data)
            if form.model.data:
                form.year.choices = get_car_years(form.make.data, form.model.data)
        
        if form.validate_on_submit():
            try:
                vehicle = Vehicle(
                    make=form.make.data,
                    model=form.model.data,
                    year=form.year.data,
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
    
    # Populate dropdowns for GET or failed POST
    if form.make.data:
        form.model.choices = get_car_models(form.make.data)
        if form.model.data:
            form.year.choices = get_car_years(form.make.data, form.model.data)
    else:
        form.model.choices = [('', 'Select Model')]
        form.year.choices = [('', 'Select Year')]
    
    return render_template('add_vehicle.html', form=form)

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
        log = RepairLog(
            mileage=form.mileage.data,
            description=form.description.data,
            vehicle_id=vehicle_id
        )
        db.session.add(log)
        db.session.commit()
        flash('Log added!', 'success')
        return redirect(url_for('view_logs', vehicle_id=vehicle_id))
    return render_template('add_log.html', form=form, vehicle=vehicle)

@app.route('/vehicle/<int:vehicle_id>/logs')
@login_required
def view_logs(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != current_user.id:
        flash('Not your vehicle.', 'danger')
        return redirect(url_for('dashboard'))
    logs = vehicle.logs.order_by(RepairLog.date.desc()).all()
    return render_template('view_logs.html', vehicle=vehicle, logs=logs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)