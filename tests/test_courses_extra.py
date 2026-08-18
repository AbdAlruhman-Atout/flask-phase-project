def register_and_login(client):
    response = client.post(
        "/register",
        data={
            "username": "courseadmin",
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(
        "/login",
        data={
            "username": "courseadmin",
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def create_course(client, name):
    response = client.post(
        "/api/courses",
        json={"name": name},
    )

    assert response.status_code == 201
    return response.get_json()["id"]


def test_course_validation_and_not_found(client):
    register_and_login(client)

    # Empty course name.
    response = client.post(
        "/courses/add",
        data={"name": ""},
    )
    assert response.status_code == 200
    assert b"Course name is required" in response.data

    # Missing course detail.
    response = client.get("/courses/99999")
    assert response.status_code == 404

    # Missing course edit page.
    response = client.get("/courses/99999/edit")
    assert response.status_code == 404

    # Missing course deletion.
    response = client.post("/courses/99999/delete")
    assert response.status_code == 404


def test_duplicate_course_html(client):
    register_and_login(client)

    create_course(client, "Python")

    response = client.post(
        "/courses/add",
        data={"name": "Python"},
    )

    assert response.status_code == 200
    assert b"That course already exists" in response.data


def test_course_edit_validation_duplicate_and_success(client):
    register_and_login(client)

    python_id = create_course(
        client,
        "Python",
    )

    create_course(
        client,
        "Flask",
    )

    # Empty name during edit.
    response = client.post(
        f"/courses/{python_id}/edit",
        data={"name": ""},
    )

    assert response.status_code == 200
    assert b"Course name is required" in response.data

    # Rename to an existing course.
    response = client.post(
        f"/courses/{python_id}/edit",
        data={"name": "Flask"},
    )

    assert response.status_code == 200
    assert b"That course already exists" in response.data

    # Successful edit.
    response = client.post(
        f"/courses/{python_id}/edit",
        data={"name": "Advanced Python"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Advanced Python" in response.data


def test_course_delete_html(client):
    register_and_login(client)

    course_id = create_course(
        client,
        "Databases",
    )

    response = client.post(
        f"/courses/{course_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Confirm it really disappeared.
    api_response = client.get(f"/api/courses/{course_id}")

    assert api_response.status_code == 404
