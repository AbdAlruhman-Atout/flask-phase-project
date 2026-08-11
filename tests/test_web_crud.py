def create_and_login_user(client):
    client.post(
        "/register",
        data={
            "username": "admin",
            "password": "password123",
        },
    )
    client.post(
        "/login",
        data={
            "username": "admin",
            "password": "password123",
        },
    )


def test_student_html_crud(client):
    create_and_login_user(client)

    create_response = client.post(
        "/students/register",
        data={
            "student_id": "1001",
            "name": "Alice",
            "email": "alice@example.com",
            "grades": "90,85,78",
        },
        follow_redirects=True,
    )
    assert create_response.status_code == 200
    assert b"Alice" in create_response.data

    update_response = client.post(
        "/students/1001/edit",
        data={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "grades": "95,90,85",
        },
        follow_redirects=True,
    )
    assert update_response.status_code == 200
    assert b"Alice Smith" in update_response.data

    delete_response = client.post(
        "/students/1001/delete",
        follow_redirects=True,
    )
    assert delete_response.status_code == 200
    assert b"No students have been registered yet" in delete_response.data


def test_course_html_crud(client):
    create_and_login_user(client)

    create_response = client.post(
        "/courses/add",
        data={"name": "Verification"},
        follow_redirects=True,
    )
    assert create_response.status_code == 200
    assert b"Verification" in create_response.data

    detail_page = client.get("/courses")
    assert b"Verification" in detail_page.data


def test_user_html_update(client):
    create_and_login_user(client)

    users_page = client.get("/users")
    assert users_page.status_code == 200
    assert b"admin" in users_page.data
