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

def test_student_search_and_pagination(client):
    create_and_login_user(client)

    for number in range(1, 13):
        response = client.post(
            "/api/students",
            json={
                "student_id": number,
                "name": f"Student {number:02d}",
                "email": f"student{number}@example.com",
                "grades": [80],
            },
        )
        assert response.status_code == 201

    search_response = client.get(
        "/students?search=Student+03"
    )

    assert search_response.status_code == 200
    assert b"Student 03" in search_response.data
    assert b"Student 04" not in search_response.data

    first_page = client.get(
        "/students?page=1&per_page=5"
    )

    assert first_page.status_code == 200
    assert b"Student 01" in first_page.data
    assert b"Student 05" in first_page.data
    assert b"Student 06" not in first_page.data

    second_page = client.get(
        "/students?page=2&per_page=5"
    )

    assert second_page.status_code == 200
    assert b"Student 06" in second_page.data
    assert b"Student 10" in second_page.data
    assert b"Student 01" not in second_page.data

def test_course_search_and_pagination(client):
    create_and_login_user(client)

    for number in range(1, 13):
        response = client.post(
            "/api/courses",
            json={
                "name": f"Course {number:02d}",
            },
        )
        assert response.status_code == 201

    search_response = client.get(
        "/courses?search=Course+03"
    )

    assert search_response.status_code == 200
    assert b"Course 03" in search_response.data
    assert b"Course 04" not in search_response.data

    first_page = client.get(
        "/courses?page=1&per_page=5"
    )

    assert first_page.status_code == 200
    assert b"Course 01" in first_page.data
    assert b"Course 05" in first_page.data
    assert b"Course 06" not in first_page.data

    second_page = client.get(
        "/courses?page=2&per_page=5"
    )

    assert second_page.status_code == 200
    assert b"Course 06" in second_page.data
    assert b"Course 10" in second_page.data
    assert b"Course 01" not in second_page.data