from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from home_services.routes import core
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') else 'you-will-never-guess'
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

app.register_blueprint(core)
db = SQLAlchemy(app)
jwt = JWTManager(app)
