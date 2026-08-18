import os


def get_database_url():
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:///students.db",
    )

    # Hosted PostgreSQL providers commonly supply
    # postgresql:// or postgres:// URLs. Use psycopg 3
    # explicitly as the SQLAlchemy database driver.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return database_url


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key",
    )

    SQLALCHEMY_DATABASE_URI = get_database_url()

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PROFILE_UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "static",
        "uploads",
        "profiles",
    )

    MAX_CONTENT_LENGTH = 3 * 1024 * 1024

    DEBUG = (
        os.getenv(
            "FLASK_DEBUG",
            "0",
        )
        == "1"
    )
