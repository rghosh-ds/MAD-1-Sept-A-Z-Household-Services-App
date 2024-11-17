from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Admin(User):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)


class Customer(User):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(120), nullable=False)


class Professional(User):
    __tablename__ = 'professionals'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    service_type = db.Column(db.String(120), nullable=False)
    experience = db.Column(db.String(120), nullable=True)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Service('{self.name}', '{self.price}', '{self.time_required}')"


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.Text, nullable=True)

    service = db.relationship('Service', backref='requests')
    customer = db.relationship('Customer', backref='requests')
    professional = db.relationship('Professional', backref='requests', lazy=True)

    def __repr__(self):
        return (f"ServiceRequest('{self.id}',"
                f" '{self.service_id}',"
                f" '{self.customer_id}',"
                f" '{self.professional_id}',"
                f" '{self.service_status}')")
