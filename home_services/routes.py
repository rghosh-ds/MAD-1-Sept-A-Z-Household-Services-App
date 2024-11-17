from flask import render_template, Flask, Blueprint

core = Blueprint('core', __name__)


@core.route('/')
def home():
    return "Hello, World!"


@core.route('/login')
def login():
    return render_template('login.html')

