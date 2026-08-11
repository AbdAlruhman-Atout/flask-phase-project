from dotenv import load_dotenv
from flask import Flask

from app.extensions import db, login_manager, migrate


def create_app(test_config=None):
    load_dotenv()

    from app.config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    from app.models import User
    from app.routes import (
        api_bp,
        auth_bp,
        courses_bp,
        students_bp,
        users_bp,
    )

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    return app
