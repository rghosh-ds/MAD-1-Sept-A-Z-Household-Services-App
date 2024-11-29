from flask import render_template, Flask, Blueprint

core = Blueprint('core', __name__)


@core.route('/')
def home():
    return render_template("home.html", css_file="home.css")


@core.route('/login')
def login():
    return render_template('login.html', css_file=None)
