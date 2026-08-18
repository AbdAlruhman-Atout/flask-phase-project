from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Course
from app.utils.auth import roles_required


courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/courses")
@login_required
def course_list():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    per_page = max(1, min(per_page, 100))

    statement = db.select(Course)

    if search:
        statement = statement.where(Course.name.ilike(f"%{search}%"))

    statement = statement.order_by(Course.name)

    pagination = db.paginate(
        statement,
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return render_template(
        "courses.html",
        courses=pagination.items,
        pagination=pagination,
        search=search,
    )


@courses_bp.route("/courses/<int:course_id>")
@login_required
def course_detail(course_id):
    course = db.session.get(Course, course_id)

    if course is None:
        abort(404)

    return render_template(
        "course_detail.html",
        course=course,
    )


@courses_bp.route("/courses/add", methods=["GET", "POST"])
@roles_required("admin", "instructor")
def add_course():
    error = None

    if request.method == "POST":
        name = request.form["name"].strip()

        if not name:
            error = "Course name is required."

        if error is None:
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


@courses_bp.route(
    "/courses/<int:course_id>/edit",
    methods=["GET", "POST"],
)
@roles_required("admin", "instructor")
def edit_course(course_id):
    course = db.session.get(Course, course_id)

    if course is None:
        abort(404)

    error = None

    if request.method == "POST":
        name = request.form["name"].strip()

        if not name:
            error = "Course name is required."

        if error is None:
            course.name = name

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                error = "That course already exists."
            else:
                return redirect(
                    url_for(
                        "courses.course_detail",
                        course_id=course.id,
                    )
                )

    return render_template(
        "edit_course.html",
        course=course,
        error=error,
    )


@courses_bp.route(
    "/courses/<int:course_id>/delete",
    methods=["POST"],
)
@roles_required("admin", "instructor")
def delete_course(course_id):
    course = db.session.get(Course, course_id)

    if course is None:
        abort(404)

    course.students.clear()
    db.session.delete(course)
    db.session.commit()

    return redirect(url_for("courses.course_list"))
