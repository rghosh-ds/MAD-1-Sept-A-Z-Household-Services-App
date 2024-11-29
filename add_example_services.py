from home_services import app, db
from home_services.models import Service


def add_example_services():
    services = [
        {"name": "AC Repair Basic", "price": 50.0, "time_required": 60, "description": "Basic AC repair service"},
        {"name": "AC Repair Advanced", "price": 100.0, "time_required": 120, "description": "Advanced AC repair service"},
        {"name": "Salon Haircut", "price": 30.0, "time_required": 45, "description": "Professional haircut service"},
        {"name": "Salon Manicure", "price": 25.0, "time_required": 30, "description": "Professional manicure service"},
        {"name": "Cleaning Basic", "price": 40.0, "time_required": 90, "description": "Basic cleaning service"},
        {"name": "Cleaning Deep", "price": 80.0, "time_required": 180, "description": "Deep cleaning service"},
        {"name": "Electrician Wiring", "price": 60.0, "time_required": 120, "description": "Wiring service"},
        {"name": "Electrician Appliance Repair", "price": 70.0, "time_required": 90, "description": "Appliance repair service"}
    ]

    with app.app_context():
        for service in services:
            new_service = Service(
                name=service["name"],
                price=service["price"],
                time_required=service["time_required"],
                description=service["description"]
            )
            db.session.add(new_service)
        db.session.commit()
        print("Example services added to the database.")


if __name__ == "__main__":
    add_example_services()