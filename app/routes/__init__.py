from app.routes.api import api_bp
from app.routes.auth import auth_bp
from app.routes.courses import courses_bp
from app.routes.students import students_bp


__all__ = [
    "api_bp",
    "auth_bp",
    "courses_bp",
    "students_bp",
]
