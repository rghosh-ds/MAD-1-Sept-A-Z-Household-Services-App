from home_services.models import ServiceRequest
from home_services.extensions import db
from home_services import app

with app.app_context():
    service_request = ServiceRequest.query.get(4)

    if service_request:
        service_request.service_status = 'Assigned'

        db.session.commit()
        print("Service request status updated successfully.")
    else:
        print("Service request not found.")
