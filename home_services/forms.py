from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from home_services.models import User
import re


def validate_password(form, field):
    password = field.data
    if (len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password)
            or not re.search(r"[0-9]", password)):
        raise ValidationError('Password must be at least 8 characters long,'
                              ' contain an uppercase letter, a lowercase letter, and a number.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CustomerRegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), validate_password])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    address = StringField('Address', validators=[DataRequired()])
    pincode = StringField('Pincode', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use. Please choose a different one.')


class ProfessionalRegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), validate_password])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    service_type = SelectField('Service Type', validators=[DataRequired()], choices=[])
    experience = StringField('Experience (in years)', validators=[DataRequired()])
    document = FileField('Attach Documents (PDF only)', validators=[DataRequired(), FileAllowed(['pdf'])])
    address = StringField('Address', validators=[DataRequired()])
    pincode = StringField('Pincode', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use. Please choose a different one.')