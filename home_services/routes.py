from flask import render_template, Blueprint, request, redirect, url_for, flash, jsonify
from home_services.forms import LoginForm
from home_services.models import User
from home_services.extensions import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import email_validator

core = Blueprint('core', __name__)


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
