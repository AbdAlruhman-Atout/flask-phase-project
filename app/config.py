import os


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key",
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///students.db",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PROFILE_UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "static",
        "uploads",
        "profiles",
    )

    # Hard request-size limit.
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
