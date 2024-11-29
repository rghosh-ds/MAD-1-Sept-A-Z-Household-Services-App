from home_services.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash)


class Customer(User):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)


class Professional(User):
    __tablename__ = 'professionals'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    service_type = db.Column(db.String(120), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    document = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.Text, nullable=True)

    service = db.relationship('Service', backref='requests')
    customer = db.relationship('Customer', backref='requests')
    professional = db.relationship('Professional', backref='requests', lazy=True)


class Admin(User):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
