from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User(username=username)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            flash(
                "That username is already registered.",
                "error",
            )

        else:
            flash(
                "Account created successfully. You can now log in.",
                "success",
            )

            return redirect(url_for("auth.login"))

    return render_template("auth_register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        statement = db.select(User).where(User.username == username)

        user = db.session.execute(statement).scalar_one_or_none()

        if user is None or not user.check_password(password):
            flash(
                "Invalid username or password.",
                "error",
            )

        else:
            login_user(user)

            flash(
                "Logged in successfully.",
                "success",
            )

            return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
