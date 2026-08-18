from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Course, Student


students_bp = Blueprint("students", __name__)


def parse_grades(grades_text):
    try:
        grades = [
            float(grade.strip()) for grade in grades_text.split(",") if grade.strip()
        ]
    except ValueError:
        return None, "Grades must be numbers separated by commas."

    if any(grade < 0 or grade > 100 for grade in grades):
        return None, "Each grade must be between 0 and 100."

    return grades, None


@students_bp.route("/")
def home():
    return render_template("index.html")


@students_bp.route(
    "/students/register",
    methods=["GET", "POST"],
)
@login_required
def register():
    error = None

    if request.method == "POST":
        name = request.form["name"].strip()
        student_id_text = request.form["student_id"].strip()
        email = request.form["email"].strip()
        grades_text = request.form["grades"].strip()

        if not name:
            error = "Name is required."
        elif not email:
            error = "Email is required."

        try:
            student_id = int(student_id_text)
        except ValueError:
            error = "Student ID must be an integer."

        grades, grades_error = parse_grades(grades_text)
        if grades_error is not None:
            error = grades_error

        if error is None:
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
                error = "The student ID or email is already registered."
            else:
                return redirect(url_for("students.student_list"))

    return render_template(
        "register.html",
        error=error,
    )


@students_bp.route("/students")
@login_required
def student_list():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Keep the page size within a reasonable range.
    per_page = max(1, min(per_page, 100))

    statement = db.select(Student)

    if search:
        statement = statement.where(Student.name.ilike(f"%{search}%"))

    statement = statement.order_by(Student.name)

    pagination = db.paginate(
        statement,
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return render_template(
        "students.html",
        students=pagination.items,
        pagination=pagination,
        search=search,
    )


@students_bp.route("/students/<int:student_id>")
@login_required
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
    "/students/<int:student_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(404)

    error = None

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        grades_text = request.form["grades"].strip()

        if not name:
            error = "Name is required."
        elif not email:
            error = "Email is required."

        grades, grades_error = parse_grades(grades_text)
        if grades_error is not None:
            error = grades_error

        if error is None:
            student.name = name
            student.email = email
            student.grades = ",".join(str(grade) for grade in grades)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                error = "That email is already registered."
            else:
                return redirect(
                    url_for(
                        "students.student_detail",
                        student_id=student.student_id,
                    )
                )

    return render_template(
        "edit_student.html",
        student=student,
        error=error,
    )


@students_bp.route(
    "/students/<int:student_id>/delete",
    methods=["POST"],
)
@login_required
def delete_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(404)

    student.courses.clear()
    db.session.delete(student)
    db.session.commit()

    return redirect(url_for("students.student_list"))


@students_bp.route(
    "/students/<int:student_id>/enroll",
    methods=["POST"],
)
@login_required
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
