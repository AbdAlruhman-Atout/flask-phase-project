from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User


users_bp = Blueprint("users", __name__)


@users_bp.route("/users")
@login_required
def user_list():
    statement = db.select(User).order_by(User.username)
    users = db.session.execute(statement).scalars().all()

    return render_template(
        "users.html",
        users=users,
    )


@users_bp.route("/users/<int:user_id>")
@login_required
def user_detail(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    return render_template(
        "user_detail.html",
        user=user,
    )


@users_bp.route(
    "/users/<int:user_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    error = None

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username:
            error = "Username is required."

        if error is None:
            user.username = username

            if password:
                user.set_password(password)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                error = "That username is already registered."
            else:
                flash("User updated successfully.", "success")
                return redirect(
                    url_for(
                        "users.user_detail",
                        user_id=user.id,
                    )
                )

    return render_template(
        "edit_user.html",
        user=user,
        error=error,
    )


@users_bp.route(
    "/users/<int:user_id>/delete",
    methods=["POST"],
)
@login_required
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    deleting_current_user = current_user.id == user.id

    if deleting_current_user:
        logout_user()

    db.session.delete(user)
    db.session.commit()

    if deleting_current_user:
        flash("Your account was deleted.", "success")
        return redirect(url_for("auth.register"))

    flash("User deleted successfully.", "success")
    return redirect(url_for("users.user_list"))
