from flask import Flask
from flask_migrate import Migrate
from home_services.routes import core
from home_services.extensions import db, bcrypt, jwt
from home_services.models import User, Customer, Professional, Service, ServiceRequest
from home_services.utils import is_authenticated, is_customer
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') else 'you-will-never-guess'
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

app.register_blueprint(core)
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
migrate = Migrate(app, db)

app.jinja_env.globals.update(is_authenticated=is_authenticated)
app.jinja_env.globals.update(is_customer=is_customer)

with app.app_context():
    db.create_all()
