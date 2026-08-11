from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Student


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


@api_bp.route("/students", methods=["GET"])
def get_students():
    statement = db.select(Student).order_by(Student.name)

    students = db.session.execute(statement).scalars().all()

    return jsonify([student_to_dict(student) for student in students]), 200


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

        name = str(data["name"]).strip()
        email = str(data["email"]).strip()

        grades = [float(grade) for grade in data["grades"]]

    except (TypeError, ValueError):
        abort(
            400,
            description=(
                "student_id must be an integer and grades " "must be a list of numbers."
            ),
        )

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

    if any(grade < 0 or grade > 100 for grade in grades):
        abort(
            400,
            description="Each grade must be between 0 and 100.",
        )

    normalized_grades = ",".join(str(grade) for grade in grades)

    student = Student(
        student_id=student_id,
        name=name,
        email=email,
        grades=normalized_grades,
    )

    try:
        db.session.add(student)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        abort(
            400,
            description=("The student ID or email is already registered."),
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
        try:
            grades = [float(grade) for grade in data["grades"]]

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

    db.session.delete(student)
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
