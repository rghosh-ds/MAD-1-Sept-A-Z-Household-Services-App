import os
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
