import os

from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import Unauthorized
from werkzeug.utils import secure_filename
from flask import current_app
import uuid


def save_document(file, user_identifier):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    unique_filename = f"{user_identifier}_{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file.save(os.path.join(upload_folder, unique_filename))
    return unique_filename


def is_authenticated():
    try:
        get_jwt_identity()
        return True
    except Unauthorized:
        return False
    except Exception as e:
        print(e)
        return False


def is_customer():
    try:
        from home_services.models import Customer
        user_id = get_jwt_identity()
        customer = Customer.query.get(user_id)
        return customer is not None
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False
    except Unauthorized:
        return False
    except Exception as e:
        print(e)


def is_professional():
    try:
        from home_services.models import Professional
        user_id = get_jwt_identity()
        professional = Professional.query.get(user_id)
        return professional is not None
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False
    except Unauthorized:
        return False
    except Exception as e:
        print(e)
        return False


def is_admin():
    try:
        from home_services.models import Admin
        user_id = get_jwt_identity()
        admin = Admin.query.get(user_id)
        return admin is not None
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False
    except Unauthorized:
        return False
    except Exception as e:
        print(e)
        return False

