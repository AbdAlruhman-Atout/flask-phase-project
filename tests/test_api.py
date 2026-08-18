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


def test_enrollment_api(client):
    student_response = client.post(
        "/api/students",
        json={
            "student_id": 100,
            "name": "Alice",
            "email": "alice@example.com",
            "grades": [90, 85],
        },
    )
    assert student_response.status_code == 201

    course_response = client.post(
        "/api/courses",
        json={"name": "Flask"},
    )
    assert course_response.status_code == 201

    course_id = course_response.get_json()["id"]

    enroll_response = client.post(f"/api/students/100/courses/{course_id}")

    assert enroll_response.status_code == 201

    data = enroll_response.get_json()

    assert len(data["courses"]) == 1
    assert data["courses"][0]["id"] == course_id
    assert data["courses"][0]["name"] == "Flask"

    duplicate_response = client.post(f"/api/students/100/courses/{course_id}")

    assert duplicate_response.status_code == 409
    assert duplicate_response.get_json()["message"] == (
        "Student is already enrolled in this course."
    )


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


def test_unenrollment_api(client):
    student_response = client.post(
        "/api/students",
        json={
            "student_id": 200,
            "name": "Bob",
            "email": "bob@example.com",
            "grades": [80, 90],
        },
    )
    assert student_response.status_code == 201

    course_response = client.post(
        "/api/courses",
        json={"name": "Databases"},
    )
    assert course_response.status_code == 201

    course_id = course_response.get_json()["id"]

    enroll_response = client.post(f"/api/students/200/courses/{course_id}")
    assert enroll_response.status_code == 201

    unenroll_response = client.delete(f"/api/students/200/courses/{course_id}")
    assert unenroll_response.status_code == 204

    student_response = client.get("/api/students/200")
    assert student_response.status_code == 200
    assert student_response.get_json()["courses"] == []

    second_unenroll = client.delete(f"/api/students/200/courses/{course_id}")
    assert second_unenroll.status_code == 404


def test_get_student_courses_api(client):
    student_response = client.post(
        "/api/students",
        json={
            "student_id": 300,
            "name": "Charlie",
            "email": "charlie@example.com",
            "grades": [75, 88],
        },
    )
    assert student_response.status_code == 201

    course1_response = client.post(
        "/api/courses",
        json={"name": "Python"},
    )
    assert course1_response.status_code == 201

    course2_response = client.post(
        "/api/courses",
        json={"name": "Flask"},
    )
    assert course2_response.status_code == 201

    course1_id = course1_response.get_json()["id"]
    course2_id = course2_response.get_json()["id"]

    assert client.post(f"/api/students/300/courses/{course1_id}").status_code == 201

    assert client.post(f"/api/students/300/courses/{course2_id}").status_code == 201

    response = client.get("/api/students/300/courses")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2

    names = {course["name"] for course in data}

    assert names == {"Python", "Flask"}
