from flask import Flask
from flask_migrate import Migrate
from home_services.routes import core
from home_services.extensions import db, bcrypt, jwt
from home_services.models import User, Customer, Professional, Service, ServiceRequest, Admin
from home_services.utils import is_authenticated, is_customer, is_professional
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


def create_admin():
    admin_email = os.getenv('ADMIN_EMAIL') if os.getenv('ADMIN_EMAIL') else "admin@homeservices.com"
    admin_password = os.getenv("ADMIN_PASSWORD") if os.getenv("ADMIN_PASSWORD") else "you-will-never-guess"
    admin_name = os.getenv("ADMIN_NAME") if os.getenv("ADMIN_NAME") else "Admin"

    if not User.query.filter_by(email=admin_email).first():
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        admin = Admin(name=admin_name, email=admin_email, password_hash=hashed_password)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")


app.jinja_env.globals.update(is_authenticated=is_authenticated)
app.jinja_env.globals.update(is_customer=is_customer)
app.jinja_env.globals.update(is_professional=is_professional)

with app.app_context():
    db.create_all()
    create_admin()
