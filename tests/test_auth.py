from app.extensions import db
from app.models import User


def register_user(
    client,
    username="abd",
    password="password123",
):
    return client.post(
        "/register",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )


def login_user(
    client,
    username="abd",
    password="password123",
):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )


def test_register_user(client, app):
    response = register_user(client)

    assert response.status_code == 200
    assert b"Account created successfully" in response.data

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(User.username == "abd")
        ).scalar_one_or_none()

        assert user is not None
        assert user.password_hash != "password123"


def test_duplicate_username(client):
    register_user(client)

    response = register_user(client)

    assert response.status_code == 200
    assert b"already registered" in response.data


def test_login_success(client):
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Logged in successfully" in response.data


def test_login_bad_password(client):
    register_user(client)

    response = login_user(
        client,
        password="wrong-password",
    )

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get(
        "/dashboard",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_logout(client):
    register_user(client)
    login_user(client)

    response = client.get(
        "/logout",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"logged out" in response.data

    dashboard_response = client.get(
        "/dashboard",
        follow_redirects=False,
    )

    assert dashboard_response.status_code == 302
