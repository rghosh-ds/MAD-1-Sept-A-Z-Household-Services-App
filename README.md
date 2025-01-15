# Project Report for Final Project
## Modern Application Development - 1

Author

Rangan Ghosh

22f3000336

I am a (B.S.-hopeful) Diploma student at IIT Madras, studying in the Data Science and Applications
Program. I enjoy making solutions using code, and also freelance on the side. This project was an exciting
endeavour, and crossing the hurdles it presented to me was a massive growth factor.

### Description
The Household Services Application is a multi-user platform designed to connect customers, service
professionals, and an admin for comprehensive home servicing solutions. Built using Flask, Jinja2
templates with Bootstrap, and SQLite, the app enables customers to search for and book services, service
professionals to manage and fulfill requests, and the admin to oversee all activities, including user
management, service creation, and request monitoring. Key features include secure login, user
registration, service request management, progress tracking, and an intuitive dashboard for all
stakeholders.

### Technologies Used
1. Flask: Used for building the core web application.
2. Flask-SQLAlchemy: An ORM extension for database management.
3. Flask-Bcrypt: Provides password hashing for secure authentication.
4. Flask-Cors: Enables cross-origin requests between frontend and backend.
5. Flask-JWT-Extended: Used for implementing authentication via JSON Web Tokens (JWTs).
6. Flask-Migrate: Handles database migrations in the application.
7. Flask-WTF: Simplifies form creation and validation in Flask.
8. Jinja2: Templating engine for rendering HTML pages.
9. SQLAlchemy: Manages database interactions and ORM functionality.
10. WTForms: For form validation and handling user inputs.
11. python-dotenv: Manages application configuration through environment variables.

### Database Schema Design
The application models a hierarchical structure of users, services, and requests with clearly defined
relationships:
User: Primary key is id. Shared attributes include email and password_hash, with specialization into
different roles.
Admin: A specialized user responsible for administrative tasks, with attributes like name.
Customer: A user who requests services, with attributes such as name, address, and pincode.
Professional: A user who provides services, with attributes like service_type, experience, and status.
Service: Represents a service with attributes like name, price, time_required, and description.
ServiceRequest: Links services, customers, and professionals, with attributes like service_status,
remarks, and rating

![image](https://github.com/user-attachments/assets/04d3a21e-a904-49c6-8947-9e72966bc594)


### API Design
Authentication:
● /login (GET, POST): Handles user login and token generation.
● /logout (POST): Logs the user out by invalidating the token.
● /register_customer (GET, POST): Registers new customers.
● /register_professional (GET, POST): Registers new professionals with approval.
Admin Actions:
● /approve_professional/<int:id> (POST): Approves a professional’s registration.
● /reject_professional/<int:id> (POST): Rejects a professional’s registration.
● /delete_professional/<int:id> (POST): Deletes a professional’s account.
Customer Actions:
● /customer_home (GET, POST): Displays customer dashboard with service history and search.
● /customer_summary (GET): Shows customer ratings and service status.
Professional Actions:
● /professional_home (GET): Displays professional dashboard with current and completed service
requests.
● /professional_summary (GET): Shows professional ratings and service request summaries.
Admin Dashboard:
● /admin_dashboard (GET, POST): Displays admin dashboard with search and manage options for
service requests and users.
