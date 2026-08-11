from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Course


courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/courses")
def course_list():
    statement = db.select(Course).order_by(Course.name)
    courses = db.session.execute(statement).scalars().all()

    return render_template(
        "courses.html",
        courses=courses,
    )


@courses_bp.route("/courses/add", methods=["GET", "POST"])
def add_course():
    error = None

    if request.method == "POST":
        name = request.form["name"].strip()
        course = Course(name=name)

        try:
            db.session.add(course)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            error = "That course already exists."
        else:
            return redirect(url_for("courses.course_list"))

    return render_template(
        "add_course.html",
        error=error,
    )
