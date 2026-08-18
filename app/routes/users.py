from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User
from app.forms import UserEditForm
from app.utils.uploads import (
    delete_profile_picture,
    save_profile_picture,
)


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

    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data.strip()

        if form.password.data:
            user.set_password(form.password.data)

        old_picture = user.profile_picture
        new_picture = None

        if form.profile_picture.data:
            new_picture = save_profile_picture(form.profile_picture.data)

            user.profile_picture = new_picture

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            if new_picture:
                delete_profile_picture(new_picture)

            flash(
                "That username is already registered.",
                "error",
            )

        else:
            if new_picture and old_picture and old_picture != new_picture:
                delete_profile_picture(old_picture)

            flash(
                "User updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "users.user_detail",
                    user_id=user.id,
                )
            )

    elif form.is_submitted():
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, "error")

    return render_template(
        "edit_user.html",
        user=user,
        form=form,
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
