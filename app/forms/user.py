from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class UserEditForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=100),
        ],
    )

    role = SelectField(
        "Role",
        choices=[
            ("admin", "Admin"),
            ("instructor", "Instructor"),
            ("student", "Student"),
        ],
        validators=[Optional()],
    )

    password = PasswordField(
        "New password",
        validators=[
            Optional(),
            Length(min=6, max=128),
        ],
    )

    profile_picture = FileField(
        "Profile picture",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "gif", "webp"],
                "Only JPG, JPEG, PNG, GIF, and WEBP images are allowed.",
            ),
            FileSize(
                max_size=2 * 1024 * 1024,
                message="Profile picture must be 2 MB or smaller.",
            ),
        ],
    )

    submit = SubmitField("Save changes")
