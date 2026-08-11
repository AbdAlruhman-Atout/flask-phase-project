# Flask Student Management Dashboard

A Flask capstone project for managing users, students, courses, enrollments, and student grades through both HTML pages and REST API endpoints.

## Features

* Flask application using Blueprints
* SQLite database with SQLAlchemy
* Three main models: `User`, `Student`, and `Course`
* Full CRUD operations for all three models
* User authentication with login and logout using Flask-Login
* Secure password hashing with Werkzeug
* HTML pages rendered with Jinja templates
* Student enrollment in courses
* Student grade management and average calculation
* REST API CRUD endpoints for students, courses, and users
* Flask test suite covering authentication, HTML CRUD, and REST API endpoints
* Database migrations using Flask-Migrate

## Project Structure

```text
flask-phase-project/
├── app/
│   ├── models/
│   │   ├── association.py
│   │   ├── course.py
│   │   ├── student.py
│   │   └── user.py
│   ├── routes/
│   │   ├── api.py
│   │   ├── auth.py
│   │   ├── courses.py
│   │   ├── students.py
│   │   └── users.py
│   ├── templates/
│   ├── __init__.py
│   ├── config.py
│   └── extensions.py
├── migrations/
├── tests/
├── .env.example
├── requirements.txt
├── run.py
└── seed.py
```

## Technologies

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Login
* Flask-Migrate
* SQLite
* Jinja2
* Werkzeug
* Pytest
* python-dotenv

## Setup

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd flask-phase-project
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Create the local environment configuration:

```bash
cp .env.example .env
```

The default development configuration uses SQLite:

```env
SECRET_KEY=change-me
DATABASE_URL=sqlite:///students.db
```

## Database Setup

Apply the existing database migrations:

```bash
python -m flask --app run.py db upgrade
```

## Running the Application

Start the Flask development server:

```bash
python run.py
```

The application runs by default at:

```text
http://127.0.0.1:5000
```

## Authentication

Users can create an account through:

```text
/register
```

Users can log in through:

```text
/login
```

Authenticated users can access the management dashboard at:

```text
/dashboard
```

Users can log out through:

```text
/logout
```

## HTML CRUD Routes

### Students

```text
GET/POST  /students/register
GET       /students
GET       /students/<student_id>
GET/POST  /students/<student_id>/edit
POST      /students/<student_id>/delete
POST      /students/<student_id>/enroll
```

The student interface supports:

* Creating students
* Viewing all students
* Viewing individual student details
* Updating student information
* Deleting students
* Managing student grades
* Enrolling students in courses

### Courses

```text
GET       /courses
GET       /courses/<course_id>
GET/POST  /courses/add
GET/POST  /courses/<course_id>/edit
POST      /courses/<course_id>/delete
```

The course interface supports:

* Creating courses
* Viewing all courses
* Viewing course details
* Updating course information
* Deleting courses
* Viewing enrolled students

### Users

```text
GET       /users
GET       /users/<user_id>
GET/POST  /users/<user_id>/edit
POST      /users/<user_id>/delete
```

User creation is handled through the authentication registration route:

```text
GET/POST  /register
```

The user management interface supports:

* Creating users
* Viewing users
* Updating usernames and passwords
* Deleting users

## REST API

The application provides REST API endpoints for all three main resources.

### Students API

```text
GET     /api/students
GET     /api/students/<student_id>
POST    /api/students
PUT     /api/students/<student_id>
DELETE  /api/students/<student_id>
```

Example student JSON:

```json
{
  "student_id": 1001,
  "name": "Alice",
  "email": "alice@example.com",
  "grades": [90, 85, 78]
}
```

### Courses API

```text
GET     /api/courses
GET     /api/courses/<course_id>
POST    /api/courses
PUT     /api/courses/<course_id>
DELETE  /api/courses/<course_id>
```

Example course JSON:

```json
{
  "name": "Digital Design"
}
```

### Users API

```text
GET     /api/users
GET     /api/users/<user_id>
POST    /api/users
PUT     /api/users/<user_id>
DELETE  /api/users/<user_id>
```

Example user JSON:

```json
{
  "username": "admin",
  "password": "password123"
}
```

Passwords are securely hashed before being stored, and password hashes are never returned by the REST API.

## Data Model

### User

Represents an authenticated application user.

Main fields:

* `id`
* `username`
* `password_hash`

### Student

Represents a student in the management system.

Main fields:

* `student_id`
* `name`
* `email`
* `grades`

Students can be enrolled in multiple courses.

### Course

Represents a course available in the system.

Main fields:

* `id`
* `name`

Courses can contain multiple students.

### Student-Course Relationship

Students and courses use a many-to-many relationship through an association table.

This allows:

* One student to enroll in multiple courses
* One course to contain multiple students

## Testing

The project includes automated tests for authentication, HTML CRUD operations, and REST API endpoints.

Run the complete test suite with:

```bash
python -m pytest
```

The tests cover functionality including:

* User registration
* Login and logout
* Authentication protection
* Student CRUD operations
* Course CRUD operations
* User CRUD operations
* Student REST API endpoints
* Course REST API endpoints
* User REST API endpoints
* Request validation
* Error handling

## Security

The application includes several basic security practices:

* Passwords are hashed using Werkzeug
* Password hashes are not exposed through the REST API
* Flask-Login manages authenticated user sessions
* Protected pages require authentication
* Sensitive local configuration is stored through environment variables

## Database Migrations

Flask-Migrate is used to manage database schema changes.

Existing migrations can be applied with:

```bash
python -m flask --app run.py db upgrade
```

The application uses SQLite for local development.

## Summary

The Flask Student Management Dashboard provides a complete web-based management system with:

* User authentication
* Student management
* Course management
* User management
* Student-course enrollment
* Grade tracking
* HTML/Jinja interfaces
* REST APIs
* Automated testing
* SQLAlchemy database integration
* Flask database migrations
