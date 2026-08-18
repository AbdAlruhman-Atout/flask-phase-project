from dotenv import load_dotenv
from flask import Flask, render_template

from app.extensions import db, login_manager, migrate, csrf


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
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    from app.models import User
    from app.routes import (
        api_bp,
        auth_bp,
        courses_bp,
        students_bp,
        users_bp,
    )

    csrf.exempt(api_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("not_found.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template("internal_server_error.html"), 500

    return app
