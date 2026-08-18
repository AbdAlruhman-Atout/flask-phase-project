from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=100),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, max=128),
        ],
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(max=128),
        ],
    )

    submit = SubmitField("Login")
