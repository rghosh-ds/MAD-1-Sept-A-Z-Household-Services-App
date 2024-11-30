import os
from datetime import timedelta

from flask import render_template, Blueprint, request, redirect, url_for, flash, jsonify, current_app, send_file
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from werkzeug.exceptions import Unauthorized

from home_services.forms import LoginForm, CustomerRegistrationForm, ProfessionalRegistrationForm
from home_services.models import User, Customer, Professional, ServiceRequest, Service, Admin
from home_services.extensions import db, bcrypt, blacklist, jwt, csrf
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import email_validator

from home_services.utils import save_document

core = Blueprint('core', __name__)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklist


@core.route('/', methods=["GET", "POST"])
def home():
    return render_template("home.html", css_file="home.css")


@core.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    error_message = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=3))
            response = None
            if Customer.query.get(user.id):
                response = redirect(url_for('core.customer_home'))
            elif professional := Professional.query.get(user.id):
                if professional.status == 'Pending':
                    error_message = 'Your account is pending approval. Please contact the admin.'
                else:
                    response = redirect(url_for('core.professional_home'))
            elif Admin.query.get(user.id):
                response = redirect(url_for('core.admin_dashboard'))
            else:
                return jsonify({'message': 'Login Error'}), 400
            if response:
                response.set_cookie('access_token_cookie', access_token, httponly=True)
                return response
        else:
            error_message = 'Login Unsuccessful. Please check email and password'
    return render_template('login.html', form=form, css_file="login.css", error_message=error_message)


@core.route('/logout', methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def logout():
    jti = get_jwt()['jti']
    blacklist.add(jti)
    response = redirect(url_for('core.home'))
    response.delete_cookie('access_token')
    return response


@core.route('/register_customer', methods=["GET", "POST"])
def register_customer():
    form = CustomerRegistrationForm()
    success_message = None
    error_message = None
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            customer = Customer(
                name=form.name.data,
                email=form.email.data,
                password_hash=hashed_password,
                address=form.address.data,
                pincode=form.pincode.data
            )
            db.session.add(customer)
            db.session.commit()
            success_message = 'Your account has been created! You are now able to log in'
            return render_template('register_customer.html', form=form, css_file="register.css",
                                   success_message=success_message)
        else:
            error_message = 'Registration Unsuccessful. Please check the form and try again.'
    return render_template('register_customer.html', form=form, css_file="register.css",
                           error_message=error_message)


@core.route('/register_professional', methods=["GET", "POST"])
def register_professional():
    form = ProfessionalRegistrationForm()
    form.service_type.choices = [(service.name, service.name) for service in Service.query.all()]
    success_message = None
    error_message = None
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            document_filename = save_document(form.document.data, form.email.data)
            professional = Professional(
                name=form.name.data,
                email=form.email.data,
                password_hash=hashed_password,
                service_type=form.service_type.data,
                experience=form.experience.data,
                document=document_filename,
                address=form.address.data,
                pincode=form.pincode.data,
                status='Pending'
            )
            db.session.add(professional)
            db.session.commit()
            success_message = 'Your registration request has been submitted. Please wait for admin approval.'
            return render_template('register_professional.html', form=form, css_file="register.css",
                                   success_message=success_message)
        else:
            error_message = 'Registration Unsuccessful. Please check the form and try again.'
    return render_template('register_professional.html', form=form, css_file="register.css",
                           error_message=error_message)


@core.route('/approve_professional/<int:professional_id>', methods=["POST"])
@jwt_required(locations=["cookies"])
def approve_professional(professional_id):
    user_id = get_jwt_identity()
    admin = Admin.query.get(user_id)
    if not admin:
        return redirect(url_for('core.login'))

    professional = Professional.query.get_or_404(professional_id)
    professional.status = 'Approved'
    db.session.commit()
    flash('Professional approved successfully!', 'success')
    return redirect(url_for('core.admin_dashboard'))


@core.route('/reject_professional/<int:professional_id>', methods=["POST"])
@jwt_required(locations=["cookies"])
def reject_professional(professional_id):
    user_id = get_jwt_identity()
    admin = Admin.query.get(user_id)
    if not admin:
        return redirect(url_for('core.login'))

    professional = Professional.query.get_or_404(professional_id)
    professional.status = 'Rejected'
    db.session.commit()
    flash('Professional rejected successfully!', 'success')
    return redirect(url_for('core.admin_dashboard'))


@core.route('/delete_professional/<int:professional_id>', methods=["POST"])
@jwt_required(locations=["cookies"])
def delete_professional(professional_id):
    user_id = get_jwt_identity()
    admin = Admin.query.get(user_id)
    if not admin:
        return redirect(url_for('core.login'))

    professional = Professional.query.get_or_404(professional_id)
    db.session.delete(professional)
    db.session.commit()
    flash('Professional deleted successfully!', 'success')
    return redirect(url_for('core.admin_dashboard'))


@core.route('/customer_home', methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def customer_home():
    user_id = get_jwt_identity()
    customer = Customer.query.get(user_id)
    if not customer:
        return redirect(url_for('core.home'))

    service_history = ServiceRequest.query.filter_by(customer_id=user_id).all()
    selected_service = request.args.get('service')
    search_by = request.args.get('search_by')
    search_text = request.args.get('search_text')
    show_search = request.args.get('search') == 'true'
    packages = []
    search_results = []

    if selected_service:
        packages = Service.query.filter(Service.name.like(f"%{selected_service}%")).all()

    if search_by and search_text:
        show_search = True
        if search_by == 'service_name':
            search_results = Service.query.filter(Service.name.like(f"%{search_text}%")).all()
        elif search_by == 'price':
            search_results = Service.query.filter(Service.price.like(f"%{search_text}%")).all()
        elif search_by == 'description':
            search_results = Service.query.filter(Service.description.like(f"%{search_text}%")).all()
        elif search_by == 'time_required':
            search_results = Service.query.filter(Service.time_required.like(f"%{search_text}%")).all()

    return render_template('customer_home.html', service_history=service_history, selected_service=selected_service,
                           packages=packages, search_results=search_results, show_search=show_search, css_file=None)


@core.route('/professional_home', methods=["GET"])
@jwt_required(locations=["cookies"])
def professional_home():
    current_user_id = get_jwt_identity()
    professional = Professional.query.get(current_user_id)
    if not professional:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('core.login'))

    ongoing_services = ServiceRequest.query.filter_by(service_status='Assigned', professional_id=professional.id).all()
    todays_services = ServiceRequest.query.filter_by(service_status='Pending').filter(
        ServiceRequest.professional_id.is_(None),
        ServiceRequest.service.has(Service.name == professional.service_type)
    ).all()

    closed_services = ServiceRequest.query.filter_by(professional_id=professional.id).filter(
        ServiceRequest.service_status.in_(['Completed', 'Cancelled'])
    ).all()

    return render_template('professional_home.html',ongoing_services=ongoing_services, todays_services=todays_services, closed_services=closed_services)


@core.route('/admin_dashboard', methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def admin_dashboard():
    user_id = get_jwt_identity()
    admin = Admin.query.get(user_id)
    if not admin:
        return redirect(url_for('core.login'))

    show_search = request.args.get('search') == 'true'
    search_by = request.args.get('search_by')
    search_text = request.args.get('search_text')

    services = Service.query.all()
    professionals = Professional.query.all()
    service_requests = ServiceRequest.query.all()
    search_results = []

    if show_search and search_by and search_text:
        if search_by == 'service_name':
            search_results = ServiceRequest.query.join(Service).filter(Service.name.ilike(f'%{search_text}%')).all()
        elif search_by == 'professional_name':
            search_results = ServiceRequest.query.join(Professional).filter(Professional.name.ilike(f'%{search_text}%')).all()
        elif search_by == 'request_status':
            search_results = ServiceRequest.query.filter(ServiceRequest.service_status.ilike(f'%{search_text}%')).all()

    return render_template('admin_dashboard.html', services=services, professionals=professionals, service_requests=service_requests, show_search=show_search, search_results=search_results)


@core.route('/add_service', methods=["POST"])
@jwt_required(locations=["cookies"])
def add_service():
    user_id = get_jwt_identity()
    admin = Admin.query.get(user_id)
    if not admin:
        return redirect(url_for('core.home'))

    service_name = request.form.get('service_name')
    service_description = request.form.get('service_description')
    service_price = request.form.get('service_price')
    service_time_required = request.form.get('service_time_required')

    new_service = Service(
        name=service_name,
        description=service_description,
        price=service_price,
        time_required=service_time_required
    )
    db.session.add(new_service)
    db.session.commit()

    return redirect(url_for('core.admin_dashboard'))


@core.route('/edit_service/<int:service_id>', methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def edit_service(service_id):
    user_id = get_jwt_identity()
    admin = Admin.query.get(user_id)
    if not admin:
        return redirect(url_for('core.login'))

    service = Service.query.get_or_404(service_id)
    if request.method == "POST":
        service.name = request.form.get('service_name')
        service.description = request.form.get('service_description')
        service.price = request.form.get('service_price')
        service.time_required = request.form.get('service_time_required')
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('core.admin_dashboard'))

    return render_template('edit_service.html', service=service)


@core.route('/delete_service/<int:service_id>', methods=["POST"])
@jwt_required(locations=["cookies"])
def delete_service(service_id):
    user_id = get_jwt_identity()
    admin = Admin.query.get(user_id)
    if not admin:
        return redirect(url_for('core.login'))

    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully!', 'success')
    return redirect(url_for('core.admin_dashboard'))


@core.route('/book_service/<int:service_id>', methods=["POST"])
@jwt_required(locations=["cookies"])
def book_service(service_id):
    user_id = get_jwt_identity()
    customer = Customer.query.get(user_id)
    if not customer:
        return redirect(url_for('core.home'))

    service = Service.query.get_or_404(service_id)
    new_request = ServiceRequest(
        service_id=service.id,
        customer_id=customer.id,
        service_status='Pending'
    )
    db.session.add(new_request)
    db.session.commit()
    flash('Service booked successfully!', 'success')
    return redirect(url_for('core.customer_home'))


@core.route('/accept_service/<int:service_id>', methods=["POST"])
@jwt_required(locations=["cookies"])
def accept_service(service_id):
    service_request = ServiceRequest.query.get_or_404(service_id)
    if service_request.professional_id is not None:
        flash('Service already accepted by another professional.', 'danger')
        return redirect(url_for('core.professional_home'))

    current_user_id = get_jwt_identity()
    professional = Professional.query.get(current_user_id)
    if not professional:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('core.professional_home'))

    service_request.professional_id = professional.id
    service_request.service_status = 'Assigned'
    db.session.commit()
    flash('Service accepted successfully.', 'success')
    return redirect(url_for('core.professional_home'))


@core.route('/professional/<int:professional_id>/details', methods=["GET"])
def view_professional_details(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    document_path = os.path.join(current_app.config['UPLOAD_FOLDER'], professional.document)
    if not os.path.exists(document_path):
        flash('Document not found', 'danger')
        return redirect(url_for('core.admin_dashboard'))
    return send_file(document_path, as_attachment=False)
