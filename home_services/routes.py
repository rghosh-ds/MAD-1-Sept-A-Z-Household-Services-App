import os

from flask import render_template, Blueprint, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from home_services.forms import LoginForm, CustomerRegistrationForm, ProfessionalRegistrationForm
from home_services.models import User, Customer, Professional
from home_services.extensions import db, bcrypt, blacklist, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import email_validator

from home_services.utils import save_document

core = Blueprint('core', __name__)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklist


@core.route('/', methods=["GET", "POST"])
def home():
    return render_template("home.html", css_file="home.css")


@core.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    error_message = None
    if form.validate_on_submit():
        print("Form submitted successfully")
        print(f"Email: {form.email.data}")
        user = User.query.filter_by(email=form.email.data).first()
        print(f"User found: {user}")
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            print("Password check passed")
            access_token = create_access_token(identity=user.id)
            return jsonify({'access_token': access_token, 'message': 'Login successful', 't': 'loginSuccess'}), 200
        else:
            print("Login unsuccessful. Invalid email or password")
            error_message = 'Login Unsuccessful. Please check email and password'
    else:
        print("Form validation failed")
    return render_template('login.html', form=form, css_file="login.css", error_message=error_message)


@jwt_required()
@core.route('/logout', methods=["POST"])
def logout():
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200


@core.route('/register_customer', methods=["GET", "POST"])
def register_customer():
    form = CustomerRegistrationForm()
    success_message = None
    error_message = None
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            customer = Customer(
                name=form.name.data,
                email=form.email.data,
                password_hash=hashed_password,
                address=form.address.data,
                pincode=form.pincode.data
            )
            db.session.add(customer)
            db.session.commit()
            success_message = 'Your account has been created! You are now able to log in'
            return render_template('register_customer.html', form=form, css_file="register.css",
                                   success_message=success_message)
        else:
            error_message = 'Registration Unsuccessful. Please check the form and try again.'
    return render_template('register_customer.html', form=form, css_file="register.css",
                           error_message=error_message)


@core.route('/register_professional', methods=["GET", "POST"])
def register_professional():
    form = ProfessionalRegistrationForm()
    success_message = None
    error_message = None
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            document_filename = save_document(form.document.data, form.email.data)
            professional = Professional(
                name=form.name.data,
                email=form.email.data,
                password_hash=hashed_password,
                service_type=form.service_type.data,
                experience=form.experience.data,
                document=document_filename,
                address=form.address.data,
                pincode=form.pincode.data
            )
            db.session.add(professional)
            db.session.commit()
            success_message = 'Your account has been created! You are now able to log in'
            return render_template('register_professional.html', form=form, css_file="register.css",
                                   success_message=success_message)
        else:
            error_message = 'Registration Unsuccessful. Please check the form and try again.'
    return render_template('register_professional.html', form=form, css_file="register.css",
                           error_message=error_message)
