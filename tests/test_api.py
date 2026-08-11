def student_payload(
    student_id=1001,
    name="Alice",
    email="alice@example.com",
    grades=None,
):
    if grades is None:
        grades = [90, 85, 78]

    return {
        "student_id": student_id,
        "name": name,
        "email": email,
        "grades": grades,
    }


def test_student_api_crud(client):
    create_response = client.post(
        "/api/students",
        json=student_payload(),
    )
    assert create_response.status_code == 201

    detail_response = client.get("/api/students/1001")
    assert detail_response.status_code == 200
    assert detail_response.get_json()["name"] == "Alice"

    update_response = client.put(
        "/api/students/1001",
        json={
            "name": "Alice Smith",
            "grades": [95, 90, 85],
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["average"] == 90.0

    delete_response = client.delete("/api/students/1001")
    assert delete_response.status_code == 204

    missing_response = client.get("/api/students/1001")
    assert missing_response.status_code == 404


def test_course_api_crud(client):
    create_response = client.post(
        "/api/courses",
        json={"name": "Digital Design"},
    )
    assert create_response.status_code == 201

    course_id = create_response.get_json()["id"]

    detail_response = client.get(f"/api/courses/{course_id}")
    assert detail_response.status_code == 200
    assert detail_response.get_json()["name"] == "Digital Design"

    update_response = client.put(
        f"/api/courses/{course_id}",
        json={"name": "Advanced Digital Design"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["name"] == "Advanced Digital Design"

    delete_response = client.delete(f"/api/courses/{course_id}")
    assert delete_response.status_code == 204


def test_user_api_crud_does_not_expose_password_hash(client):
    create_response = client.post(
        "/api/users",
        json={
            "username": "admin",
            "password": "secret123",
        },
    )
    assert create_response.status_code == 201

    data = create_response.get_json()
    user_id = data["id"]

    assert data["username"] == "admin"
    assert "password" not in data
    assert "password_hash" not in data

    detail_response = client.get(f"/api/users/{user_id}")
    assert detail_response.status_code == 200

    update_response = client.put(
        f"/api/users/{user_id}",
        json={"username": "manager"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["username"] == "manager"

    delete_response = client.delete(f"/api/users/{user_id}")
    assert delete_response.status_code == 204


def test_api_lists_all_resources(client):
    client.post(
        "/api/students",
        json=student_payload(),
    )
    client.post(
        "/api/courses",
        json={"name": "Computer Architecture"},
    )
    client.post(
        "/api/users",
        json={
            "username": "tester",
            "password": "password123",
        },
    )

    assert len(client.get("/api/students").get_json()) == 1
    assert len(client.get("/api/courses").get_json()) == 1
    assert len(client.get("/api/users").get_json()) == 1


def test_api_validation_and_not_found(client):
    bad_student = client.post(
        "/api/students",
        json={
            "student_id": 1001,
            "name": "Alice",
        },
    )
    assert bad_student.status_code == 400

    bad_course = client.post(
        "/api/courses",
        json={"name": ""},
    )
    assert bad_course.status_code == 400

    bad_user = client.post(
        "/api/users",
        json={
            "username": "",
            "password": "password123",
        },
    )
    assert bad_user.status_code == 400

    missing = client.get("/api/students/9999")
    assert missing.status_code == 404
    assert missing.get_json()["error"] == "not_found"
