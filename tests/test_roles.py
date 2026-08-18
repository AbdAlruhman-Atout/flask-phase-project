from app.extensions import db
from app.models import User


def register_user(client, username):
    return client.post(
        "/register",
        data={
            "username": username,
            "password": "password123",
        },
        follow_redirects=True,
    )


def login_user(client, username):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": "password123",
        },
        follow_redirects=True,
    )


def logout_user(client):
    return client.get(
        "/logout",
        follow_redirects=True,
    )


def test_first_registered_user_is_admin(client, app):
    response = register_user(client, "firstadmin")

    assert response.status_code == 200

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(User.username == "firstadmin")
        ).scalar_one()

        assert user.role == "admin"


def test_later_registered_user_is_student(client, app):
    register_user(client, "admin")
    register_user(client, "studentuser")

    with app.app_context():
        student_user = db.session.execute(
            db.select(User).where(User.username == "studentuser")
        ).scalar_one()

        assert student_user.role == "student"

    login_user(client, "studentuser")

    # Students may view students and courses.
    assert client.get("/students").status_code == 200
    assert client.get("/courses").status_code == 200

    # Students may not modify them.
    assert (
        client.post(
            "/courses/add",
            data={"name": "Forbidden Course"},
        ).status_code
        == 403
    )

    assert (
        client.post(
            "/students/register",
            data={
                "student_id": "999",
                "name": "Forbidden Student",
                "email": "forbidden@example.com",
                "grades": "90",
            },
        ).status_code
        == 403
    )

    # User management is Admin-only.
    assert client.get("/users").status_code == 403


def test_instructor_permissions(client, app):
    register_user(client, "admin")
    register_user(client, "teacher")

    with app.app_context():
        teacher = db.session.execute(
            db.select(User).where(User.username == "teacher")
        ).scalar_one()

        teacher.role = "instructor"
        db.session.commit()

    login_user(client, "teacher")

    # Instructor can manage courses.
    response = client.post(
        "/courses/add",
        data={"name": "Instructor Course"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Instructor Course" in response.data

    # Instructor can manage students.
    response = client.post(
        "/students/register",
        data={
            "student_id": "5001",
            "name": "Instructor Student",
            "email": "instructor-student@example.com",
            "grades": "90,80",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Instructor Student" in response.data

    # Instructor cannot manage application users.
    assert client.get("/users").status_code == 403


def test_admin_can_change_user_role(client, app):
    register_user(client, "admin")
    register_user(client, "newteacher")

    login_user(client, "admin")

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(User.username == "newteacher")
        ).scalar_one()

        user_id = user.id

    response = client.post(
        f"/users/{user_id}/edit",
        data={
            "username": "newteacher",
            "role": "instructor",
            "password": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = db.session.get(User, user_id)

        assert user.role == "instructor"
