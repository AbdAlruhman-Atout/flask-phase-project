from flask import Blueprint, abort, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Course, Student


students_bp = Blueprint("students", __name__)


@students_bp.route("/")
def home():
    return render_template("index.html")


@students_bp.route(
    "/students/register",
    methods=["GET", "POST"],
)
def register():
    error = None

    if request.method == "POST":
        name = request.form["name"].strip()
        student_id_text = request.form["student_id"].strip()
        email = request.form["email"].strip()
        grades_text = request.form["grades"].strip()

        try:
            student_id = int(student_id_text)

            grades = [
                float(grade.strip())
                for grade in grades_text.split(",")
                if grade.strip()
            ]

            if any(grade < 0 or grade > 100 for grade in grades):
                error = "Each grade must be between 0 and 100."

        except ValueError:
            error = (
                "Student ID must be an integer and grades must be "
                "numbers separated by commas."
            )

        if error is None:
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
                error = "The student ID or email is already registered."
            else:
                return redirect(url_for("students.student_list"))

    return render_template(
        "register.html",
        error=error,
    )


@students_bp.route("/students")
def student_list():
    statement = db.select(Student).order_by(Student.name)
    students = db.session.execute(statement).scalars().all()

    return render_template(
        "students.html",
        students=students,
    )


@students_bp.route("/students/<int:student_id>")
def student_detail(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(404)

    statement = db.select(Course).order_by(Course.name)
    courses = db.session.execute(statement).scalars().all()

    return render_template(
        "student_detail.html",
        student=student,
        courses=courses,
    )


@students_bp.route(
    "/students/<int:student_id>/enroll",
    methods=["POST"],
)
def enroll_student(student_id):
    course_id = request.form.get("course_id", type=int)

    if course_id is None:
        abort(400)

    student = db.session.get(Student, student_id)
    course = db.session.get(Course, course_id)

    if student is None or course is None:
        abort(404)

    if course not in student.courses:
        student.courses.append(course)
        db.session.commit()

    return redirect(
        url_for(
            "students.student_detail",
            student_id=student.student_id,
        )
    )


@students_bp.errorhandler(404)
def page_not_found(error):
    return render_template("not_found.html"), 404
