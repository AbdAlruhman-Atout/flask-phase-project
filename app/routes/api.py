from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Course, Student, User


api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api",
)


def student_to_dict(student):
    return {
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "grades": student.get_grades(),
        "average": student.average,
        "courses": [
            {
                "id": course.id,
                "name": course.name,
            }
            for course in student.courses
        ],
    }


def course_to_dict(course):
    return {
        "id": course.id,
        "name": course.name,
        "students": [
            {
                "student_id": student.student_id,
                "name": student.name,
            }
            for student in course.students
        ],
    }


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "profile_picture": user.profile_picture,
    }


def parse_grade_list(value):
    if not isinstance(value, list):
        abort(
            400,
            description="Grades must be a list of numbers.",
        )

    try:
        grades = [float(grade) for grade in value]
    except (TypeError, ValueError):
        abort(
            400,
            description="Grades must be a list of numbers.",
        )

    if any(grade < 0 or grade > 100 for grade in grades):
        abort(
            400,
            description="Each grade must be between 0 and 100.",
        )

    return grades


@api_bp.route("/students", methods=["GET"])
def get_students():
    statement = db.select(Student).order_by(Student.name)
    students = db.session.execute(statement).scalars().all()

    return jsonify([student_to_dict(student) for student in students]), 200


@api_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(
            404,
            description="Student not found.",
        )

    return jsonify(student_to_dict(student)), 200


@api_bp.route("/students", methods=["POST"])
def create_student():
    data = request.get_json(silent=True)

    if data is None:
        abort(
            400,
            description="Request body must contain valid JSON.",
        )

    required_fields = {
        "student_id",
        "name",
        "email",
        "grades",
    }
    missing_fields = required_fields - data.keys()

    if missing_fields:
        abort(
            400,
            description=(
                "Missing required fields: " + ", ".join(sorted(missing_fields))
            ),
        )

    try:
        student_id = int(data["student_id"])
    except (TypeError, ValueError):
        abort(
            400,
            description="student_id must be an integer.",
        )

    name = str(data["name"]).strip()
    email = str(data["email"]).strip()
    grades = parse_grade_list(data["grades"])

    if not name:
        abort(
            400,
            description="Name cannot be empty.",
        )

    if not email:
        abort(
            400,
            description="Email cannot be empty.",
        )

    student = Student(
        student_id=student_id,
        name=name,
        email=email,
        grades=",".join(str(grade) for grade in grades),
    )

    try:
        db.session.add(student)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        abort(
            400,
            description="The student ID or email is already registered.",
        )

    return jsonify(student_to_dict(student)), 201


@api_bp.route(
    "/students/<int:student_id>",
    methods=["PUT"],
)
def update_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(
            404,
            description="Student not found.",
        )

    data = request.get_json(silent=True)

    if data is None:
        abort(
            400,
            description="Request body must contain valid JSON.",
        )

    allowed_fields = {
        "name",
        "email",
        "grades",
    }

    if not any(field in data for field in allowed_fields):
        abort(
            400,
            description=(
                "Provide at least one field to update: " "name, email, or grades."
            ),
        )

    if "name" in data:
        name = str(data["name"]).strip()

        if not name:
            abort(
                400,
                description="Name cannot be empty.",
            )

        student.name = name

    if "email" in data:
        email = str(data["email"]).strip()

        if not email:
            abort(
                400,
                description="Email cannot be empty.",
            )

        student.email = email

    if "grades" in data:
        grades = parse_grade_list(data["grades"])
        student.grades = ",".join(str(grade) for grade in grades)

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        abort(
            400,
            description="That email is already registered.",
        )

    return jsonify(student_to_dict(student)), 200


@api_bp.route(
    "/students/<int:student_id>",
    methods=["DELETE"],
)
def delete_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(
            404,
            description="Student not found.",
        )

    student.courses.clear()
    db.session.delete(student)
    db.session.commit()

    return "", 204


@api_bp.route(
    "/students/<int:student_id>/courses/<int:course_id>",
    methods=["POST"],
)
def enroll_student_in_course(student_id, course_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(
            404,
            description="Student not found.",
        )

    course = db.session.get(Course, course_id)

    if course is None:
        abort(
            404,
            description="Course not found.",
        )

    if course in student.courses:
        return (
            jsonify(
                {
                    "error": "conflict",
                    "message": "Student is already enrolled in this course.",
                }
            ),
            409,
        )

    student.courses.append(course)
    db.session.commit()

    return jsonify(student_to_dict(student)), 201


@api_bp.route(
    "/students/<int:student_id>/courses/<int:course_id>",
    methods=["DELETE"],
)
def unenroll_student_from_course(student_id, course_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(
            404,
            description="Student not found.",
        )

    course = db.session.get(Course, course_id)

    if course is None:
        abort(
            404,
            description="Course not found.",
        )

    if course not in student.courses:
        abort(
            404,
            description="Student is not enrolled in this course.",
        )

    student.courses.remove(course)
    db.session.commit()

    return "", 204


@api_bp.route(
    "/students/<int:student_id>/courses",
    methods=["GET"],
)
def get_student_courses(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(
            404,
            description="Student not found.",
        )

    courses = sorted(
        student.courses,
        key=lambda course: course.name,
    )

    return (
        jsonify(
            [
                {
                    "id": course.id,
                    "name": course.name,
                }
                for course in courses
            ]
        ),
        200,
    )


@api_bp.route("/courses", methods=["GET"])
def get_courses():
    statement = db.select(Course).order_by(Course.name)
    courses = db.session.execute(statement).scalars().all()

    return jsonify([course_to_dict(course) for course in courses]), 200


@api_bp.route("/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    course = db.session.get(Course, course_id)

    if course is None:
        abort(
            404,
            description="Course not found.",
        )

    return jsonify(course_to_dict(course)), 200


@api_bp.route("/courses", methods=["POST"])
def create_course():
    data = request.get_json(silent=True)

    if data is None:
        abort(
            400,
            description="Request body must contain valid JSON.",
        )

    if "name" not in data:
        abort(
            400,
            description="Missing required field: name.",
        )

    name = str(data["name"]).strip()

    if not name:
        abort(
            400,
            description="Course name cannot be empty.",
        )

    course = Course(name=name)

    try:
        db.session.add(course)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        abort(
            400,
            description="That course already exists.",
        )

    return jsonify(course_to_dict(course)), 201


@api_bp.route("/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    course = db.session.get(Course, course_id)

    if course is None:
        abort(
            404,
            description="Course not found.",
        )

    data = request.get_json(silent=True)

    if data is None:
        abort(
            400,
            description="Request body must contain valid JSON.",
        )

    if "name" not in data:
        abort(
            400,
            description="Provide the name field to update.",
        )

    name = str(data["name"]).strip()

    if not name:
        abort(
            400,
            description="Course name cannot be empty.",
        )

    course.name = name

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        abort(
            400,
            description="That course already exists.",
        )

    return jsonify(course_to_dict(course)), 200


@api_bp.route("/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    course = db.session.get(Course, course_id)

    if course is None:
        abort(
            404,
            description="Course not found.",
        )

    course.students.clear()
    db.session.delete(course)
    db.session.commit()

    return "", 204


@api_bp.route("/users", methods=["GET"])
def get_users():
    statement = db.select(User).order_by(User.username)
    users = db.session.execute(statement).scalars().all()

    return jsonify([user_to_dict(user) for user in users]), 200


@api_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(
            404,
            description="User not found.",
        )

    return jsonify(user_to_dict(user)), 200


@api_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)

    if data is None:
        abort(
            400,
            description="Request body must contain valid JSON.",
        )

    required_fields = {"username", "password"}
    missing_fields = required_fields - data.keys()

    if missing_fields:
        abort(
            400,
            description=(
                "Missing required fields: " + ", ".join(sorted(missing_fields))
            ),
        )

    username = str(data["username"]).strip()
    password = str(data["password"])

    if not username:
        abort(
            400,
            description="Username cannot be empty.",
        )

    if not password:
        abort(
            400,
            description="Password cannot be empty.",
        )

    user = User(username=username)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        abort(
            400,
            description="That username is already registered.",
        )

    return jsonify(user_to_dict(user)), 201


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(
            404,
            description="User not found.",
        )

    data = request.get_json(silent=True)

    if data is None:
        abort(
            400,
            description="Request body must contain valid JSON.",
        )

    allowed_fields = {"username", "password"}

    if not any(field in data for field in allowed_fields):
        abort(
            400,
            description=(
                "Provide at least one field to update: " "username or password."
            ),
        )

    if "username" in data:
        username = str(data["username"]).strip()

        if not username:
            abort(
                400,
                description="Username cannot be empty.",
            )

        user.username = username

    if "password" in data:
        password = str(data["password"])

        if not password:
            abort(
                400,
                description="Password cannot be empty.",
            )

        user.set_password(password)

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        abort(
            400,
            description="That username is already registered.",
        )

    return jsonify(user_to_dict(user)), 200


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(
            404,
            description="User not found.",
        )

    db.session.delete(user)
    db.session.commit()

    return "", 204


@api_bp.errorhandler(400)
def bad_request(error):
    return (
        jsonify(
            {
                "error": "bad_request",
                "message": error.description,
            }
        ),
        400,
    )


@api_bp.errorhandler(404)
def not_found(error):
    return (
        jsonify(
            {
                "error": "not_found",
                "message": error.description,
            }
        ),
        404,
    )


@api_bp.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()

    return (
        jsonify(
            {
                "error": "internal_server_error",
                "message": "An unexpected server error occurred.",
            }
        ),
        500,
    )
