from io import BytesIO
from pathlib import Path

from app.extensions import db
from app.models import User


def register_and_login(client):
    response = client.post(
        "/register",
        data={
            "username": "uploaduser",
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(
        "/login",
        data={
            "username": "uploaduser",
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_profile_picture_upload(client, app):
    register_and_login(client)

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(
                User.username == "uploaduser"
            )
        ).scalar_one()
        user_id = user.id

    response = client.post(
        f"/users/{user_id}/edit",
        data={
            "username": "uploaduser",
            "password": "",
            "profile_picture": (
                BytesIO(b"fake image contents"),
                "profile.png",
            ),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = db.session.get(User, user_id)

        assert user.profile_picture is not None
        assert user.profile_picture.endswith(".png")

        filename = Path(user.profile_picture).name

        saved_file = (
            Path(app.config["PROFILE_UPLOAD_FOLDER"])
            / filename
        )

        assert saved_file.exists()


def test_invalid_profile_picture_type(client, app):
    register_and_login(client)

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(
                User.username == "uploaduser"
            )
        ).scalar_one()
        user_id = user.id

    response = client.post(
        f"/users/{user_id}/edit",
        data={
            "username": "uploaduser",
            "password": "",
            "profile_picture": (
                BytesIO(b"bad file"),
                "malware.exe",
            ),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Only JPG, JPEG, PNG, GIF, and WEBP" in response.data


def test_custom_404_page(client):
    response = client.get(
        "/definitely-does-not-exist"
    )

    assert response.status_code == 404
