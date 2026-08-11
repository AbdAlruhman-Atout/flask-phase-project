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


def test_get_students_returns_empty_list(client):
    response = client.get("/api/students")

    assert response.status_code == 200
    assert response.get_json() == []


def test_create_student(client):
    response = client.post(
        "/api/students",
        json=student_payload(),
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["student_id"] == 1001
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["grades"] == [90.0, 85.0, 78.0]
    assert data["average"] == 84.33


def test_created_student_appears_in_get(client):
    client.post(
        "/api/students",
        json=student_payload(),
    )

    response = client.get("/api/students")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["student_id"] == 1001
    assert data[0]["name"] == "Alice"


def test_update_student(client):
    client.post(
        "/api/students",
        json=student_payload(),
    )

    response = client.put(
        "/api/students/1001",
        json={
            "name": "Alice Smith",
            "grades": [95, 90, 85],
        },
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["name"] == "Alice Smith"
    assert data["grades"] == [95.0, 90.0, 85.0]
    assert data["average"] == 90.0


def test_delete_student(client):
    client.post(
        "/api/students",
        json=student_payload(),
    )

    delete_response = client.delete("/api/students/1001")

    list_response = client.get("/api/students")

    assert delete_response.status_code == 204
    assert delete_response.data == b""
    assert list_response.get_json() == []


def test_update_missing_student_returns_404(client):
    response = client.put(
        "/api/students/9999",
        json={
            "name": "Missing Student",
        },
    )

    data = response.get_json()

    assert response.status_code == 404
    assert data["error"] == "not_found"
    assert data["message"] == "Student not found."


def test_delete_missing_student_returns_404(client):
    response = client.delete("/api/students/9999")

    data = response.get_json()

    assert response.status_code == 404
    assert data["error"] == "not_found"


def test_create_student_with_missing_fields_returns_400(client):
    response = client.post(
        "/api/students",
        json={
            "student_id": 1001,
            "name": "Alice",
        },
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "bad_request"
    assert "Missing required fields" in data["message"]


def test_create_student_with_invalid_grades_returns_400(client):
    response = client.post(
        "/api/students",
        json=student_payload(
            grades=["good", "bad"],
        ),
    )

    assert response.status_code == 400


def test_create_student_with_out_of_range_grade_returns_400(client):
    response = client.post(
        "/api/students",
        json=student_payload(
            grades=[90, 105],
        ),
    )

    assert response.status_code == 400


def test_duplicate_student_returns_400(client):
    payload = student_payload()

    first_response = client.post(
        "/api/students",
        json=payload,
    )

    second_response = client.post(
        "/api/students",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


def test_update_duplicate_email_returns_400(client):
    client.post(
        "/api/students",
        json=student_payload(),
    )

    client.post(
        "/api/students",
        json=student_payload(
            student_id=1002,
            name="Bob",
            email="bob@example.com",
        ),
    )

    response = client.put(
        "/api/students/1002",
        json={
            "email": "alice@example.com",
        },
    )

    assert response.status_code == 400
